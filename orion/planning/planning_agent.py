import re
from typing import List, Optional, Callable
import os
from dotenv import load_dotenv
from orion.agent_core.agents import build_agent
from orion.planning.graph_inspector import GraphInspector
from orion.memory_core.execution_memory import ExecutionMemory
from prompts import (
    PLANNING_SYSTEM_PROMPT,
    REVISION_SYSTEM_PROMPT,
    PROMPT_OPTIMIZER_SYSTEM_PROMPT,
    PLAN_CREATION_PROMPT_TEMPLATE,
    PLAN_REVISION_PROMPT_TEMPLATE
)

load_dotenv()

# Fallback template used in this module
FALLBACK_PLAN_TEMPLATE = """# Plan for: {user_request}

## Tasks
- [ ] Execute primary actions for: {user_request} using available graph capabilities
- [ ] Generate comprehensive response based on collected information"""


async def optimize_planning_prompt(
    *,
    default_system_prompt: str,
    user_instructions: str,
    llm_model: str,
    base_url: str,
    api_key: str
) -> str:
    """Return an updated planning system prompt incorporating *user_instructions*.

    The function spins up a transient "prompt-engineer" LLM to weave the extra
    guidance into the existing prompt. It returns **only** the new prompt.
    """

    # Pass the parameters as user input instead of system prompt formatting
    combined_prompt = f"USER INSTRUCTIONS:\n{user_instructions.strip()}\n\nCURRENT SYSTEM PROMPT:\n{default_system_prompt.strip()}"

    optimiser_agent = build_agent(
        llm_model=llm_model,
        base_url=base_url,
        api_key=api_key,
        system_prompt=PROMPT_OPTIMIZER_SYSTEM_PROMPT,
        stream=False,
        exponential_backoff_retry=True,
    )

    print(default_system_prompt)
    print("-" * 100)
    result = await optimiser_agent(prompt=combined_prompt)
    print(result)

    return result.strip()


class PlanningAgent:
    """
    Dynamic planning agent with ReAct-style reasoning and plan revision capabilities.
    Uses brainstorming and introspection before creating plans.
    """
    planning_agent: Optional[Callable]
    revision_agent: Optional[Callable]
    final_system_prompt: Optional[str]
    
    def __init__(
        self,
        graph_inspector: GraphInspector,
        revision_frequency: int = 1,
        *,
        optimize_prompt: bool = False,
        user_instructions: Optional[str] = None,
    ):
        """
        Initialize with LLM config and graph inspector
        
        Args:
            graph_inspector: Inspector for understanding graph capabilities
            revision_frequency: Number of tasks to complete before revising plan (default: 1 = after each task)
        """
        self.graph_inspector = graph_inspector
        self.revision_frequency = revision_frequency
        self.tasks_since_revision = 0
        
        # These will be initialized in the factory `create` method
        self.planning_agent = None
        self.revision_agent = None
        self.final_system_prompt = None

    @classmethod
    async def create(
        cls,
        graph_inspector: GraphInspector,
        revision_frequency: int = 1,
        *,
        optimize_prompt: bool = False,
        user_instructions: Optional[str] = None,
    ):
        """
        Create and initialize a PlanningAgent instance.
        
        This factory method handles the async initialization of the agent,
        including the prompt optimization.
        
        Args:
            graph_inspector: Inspector for understanding graph capabilities
            revision_frequency: Number of tasks to complete before revising plan (default: 1 = after each task)
            optimize_prompt: Whether to optimize the planning system prompt
            user_instructions: User-supplied instructions for optimizing the planning system prompt
        """
        instance = cls(graph_inspector, revision_frequency)
        
        # Figure out which system prompt to use – optimise if requested
        base_system_prompt = instance._get_base_planning_system_prompt()
        final_system_prompt = base_system_prompt

        if optimize_prompt and user_instructions:
            final_system_prompt = await optimize_planning_prompt(
                    default_system_prompt=base_system_prompt,
                    user_instructions=user_instructions,
                    llm_model=os.getenv("PLANNING_MODEL"), #type: ignore
                    base_url=os.getenv("BASE_URL"), #type: ignore
                    api_key=os.getenv("GEMINI_API_KEY"), #type: ignore
                )


        # Create LLM agents with the (possibly optimised) prompt
        instance.planning_agent = instance._create_planning_agent(final_system_prompt)
        instance.revision_agent = instance._create_revision_agent()
        
        return instance

    def _get_base_planning_system_prompt(self) -> str:
        """Return the default system prompt string for the planning agent."""
        return PLANNING_SYSTEM_PROMPT

    def _create_planning_agent(self, system_prompt: str):
        """Instantiate the planning LLM agent with the provided system prompt."""

        return build_agent(
            api_key=os.getenv("GEMINI_API_KEY"), #type: ignore
            base_url=os.getenv("BASE_URL"), #type: ignore
            llm_model=os.getenv("PLANNING_MODEL"), #type: ignore
            system_prompt=system_prompt,
        )

    def _create_revision_agent(self):
        """Create the plan revision agent that understands execution memory format"""
        return build_agent(
            api_key=os.getenv("GEMINI_API_KEY"), #type: ignore
            base_url=os.getenv("BASE_URL"), #type: ignore
            llm_model=os.getenv("PLANNING_MODEL"), #type: ignore
            system_prompt=REVISION_SYSTEM_PROMPT,
        )

    async def create_executable_plan(self, user_request: str) -> str:
        """Create initial strategic plan with ReAct-style reasoning"""
        graph_capabilities = self.graph_inspector.get_available_capabilities()
        
        # Get execution summary for references
        execution_summary = "No previous work completed."
        if hasattr(self, '_execution_memory') and self._execution_memory:
            execution_summary = self._execution_memory.get_summary_for_orchestrator()
        
        prompt = PLAN_CREATION_PROMPT_TEMPLATE.format(
            graph_capabilities=graph_capabilities,
            execution_summary=execution_summary,
            user_request=user_request
        )

        try:
            if not self.planning_agent:
                raise RuntimeError("Planning agent not initialized. Call `create` to instantiate.")
            response = await self.planning_agent(prompt=prompt)
            full_response = response
            
            # Extract just the plan portion for execution
            plan_match = re.search(r'<plan>\s*(.*?)\s*</plan>', full_response, re.DOTALL)
            if plan_match:
                plan_content = plan_match.group(1).strip()
                # Save the reasoning for reference
                self._last_reasoning = full_response
            else:
                # Fallback if tags not found - try to extract from end
                plan_content = full_response.split('<plan>')[-1].strip()
                if '</plan>' in plan_content:
                    plan_content = plan_content.split('</plan>')[0].strip()
                self._last_reasoning = full_response
            
            self.tasks_since_revision = 0

            return plan_content
            
        except Exception as e:
            print(f"Error creating executable plan: {e}")
            return self._create_fallback_plan(user_request)

    async def revise_plan(
        self, 
        current_plan: str, 
        execution_memory: ExecutionMemory,
        original_request: str,
        force: bool = False
    ) -> str:
        """
        Revise the plan based on execution progress using ReAct-style reflection
        """
        # Check if revision is needed
        if not force and self.tasks_since_revision < self.revision_frequency:
            return current_plan
            
        # Get memory entries with summaries (except for user input which remains full)
        memory_entries = execution_memory.get_planning_memory_entries()
        
        execution_history = "\n".join(memory_entries) if memory_entries else "No execution history yet."
        
        graph_capabilities = self.graph_inspector.get_available_capabilities()
        
        prompt = PLAN_REVISION_PROMPT_TEMPLATE.format(
            original_request=original_request,
            current_plan=current_plan,
            execution_history=execution_history,
            graph_capabilities=graph_capabilities
        )

        try:
            if not self.revision_agent:
                raise RuntimeError("Revision agent not initialized. Call `create` to instantiate.")
            response = await self.revision_agent(prompt=prompt)
            full_response = response
            
            # Extract revised plan
            plan_match = re.search(r'<revised_plan>\s*(.*?)\s*</revised_plan>', full_response, re.DOTALL)
            if plan_match:
                revised_plan = plan_match.group(1).strip()
                self._last_revision_reasoning = full_response
            else:
                # Fallback extraction
                revised_plan = full_response.split('<revised_plan>')[-1].strip()
                if '</revised_plan>' in revised_plan:
                    revised_plan = revised_plan.split('</revised_plan>')[0].strip()
                self._last_revision_reasoning = full_response
            
            self.tasks_since_revision = 0
            return revised_plan
            
        except Exception as e:
            print(f"Error revising plan: {e}")
            return current_plan  # Keep current plan if revision fails

    def update_plan_status(self, plan_content: str, completed_task: str) -> str:
        """Update plan to mark task as completed using pattern matching"""
        # Pattern to match unchecked task items
        unchecked_pattern = r'- \[ \] (.+)'
        
        # Find all unchecked tasks
        matches = re.findall(unchecked_pattern, plan_content)
        
        # Find the best match for the completed task
        best_match = None
        best_score = 0
        
        for task in matches:
            # Simple similarity check - count common words
            task_words = set(task.lower().split())
            completed_words = set(completed_task.lower().split())
            common_words = task_words.intersection(completed_words)
            score = len(common_words) / max(len(task_words), len(completed_words))
            
            if score > best_score and score > 0.3:  # Minimum similarity threshold
                best_match = task
                best_score = score
        
        if best_match:
            # Replace the unchecked item with checked item
            old_line = f"- [ ] {best_match}"
            new_line = f"- [x] {best_match}"
            updated_plan = plan_content.replace(old_line, new_line, 1)
            return updated_plan
        
        return plan_content

    def extract_tasks_from_plan(self, plan_content: str) -> List[str]:
        """Extract all tasks from plan content"""
        task_pattern = r'- \[[x ]\] (.+)'
        matches = re.findall(task_pattern, plan_content)
        return [task.strip() for task in matches if task.strip()]

    def get_pending_tasks(self, plan_content: str) -> List[str]:
        """Extract pending/incomplete tasks"""
        pending_pattern = r'- \[ \] (.+)'
        matches = re.findall(pending_pattern, plan_content)
        return [task.strip() for task in matches if task.strip()]

    def get_completed_tasks(self, plan_content: str) -> List[str]:
        """Extract completed tasks"""
        completed_pattern = r'- \[x\] (.+)'
        matches = re.findall(completed_pattern, plan_content)
        return [task.strip() for task in matches if task.strip()]

    def get_last_reasoning(self) -> Optional[str]:
        """Get the last reasoning/brainstorming output"""
        return getattr(self, '_last_reasoning', None)

    def get_last_revision_reasoning(self) -> Optional[str]:
        """Get the last revision reasoning output"""
        return getattr(self, '_last_revision_reasoning', None)

    def _create_fallback_plan(self, user_request: str) -> str:
        """Create a fallback plan if planning fails"""
        return FALLBACK_PLAN_TEMPLATE.format(user_request=user_request)

    def set_execution_memory(self, execution_memory: ExecutionMemory) -> None:
        """Set the execution memory for reference support."""
        self._execution_memory = execution_memory