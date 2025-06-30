import logging
from typing import Optional

from orion.graph_core.compiled_graph import CompiledGraph
from orion.planning.graph_inspector import GraphInspector
from orion.planning.planning_agent import PlanningAgent

logger = logging.getLogger(__name__)


class PlanningExecutor:
    """
    Executor that uses dynamic planning with ReAct-style reasoning and plan revision.
    Plans are revised based on execution memory observations.
    """
    
    def __init__(self, compiled_graph: "CompiledGraph"):
        """
        Initialize the dynamic planning executor
        
        Args:
            compiled_graph: The compiled graph to execute
        """
        self.compiled_graph = compiled_graph
        self.graph_inspector = GraphInspector(compiled_graph)
        self.planning_agent: Optional[PlanningAgent] = None
        
        # Track planning state
        self.current_plan = None
        self.original_request = None
        self.plan_file = "PLAN.md"

    @classmethod
    async def create(
        cls, 
        compiled_graph: "CompiledGraph", 
        revision_frequency: int = 1, 
        optimize_prompt: bool = False, 
        user_instructions: Optional[str] = None
    ) -> "PlanningExecutor":
        """
        Create a new instance of the planning executor.
        """
        executor = cls(compiled_graph)
        executor.planning_agent = await PlanningAgent.create(
            graph_inspector=executor.graph_inspector,
            revision_frequency=revision_frequency,
            optimize_prompt=optimize_prompt,
            user_instructions=user_instructions,
        )
        return executor

    async def execute_with_dynamic_planning(
        self, 
        user_request: str,
        save_plan_history: bool = True
    ) -> str:
        """
        Execute request with dynamic planning and plan revision
        
        Args:
            user_request: The user's request
            save_plan_history: Whether to save plan revision history
            
        Returns:
            Final response to the user
        """
        self.original_request = user_request
        
        print(f"🎯 Starting dynamic planning execution for: {user_request}")
        
        # Create initial plan with ReAct reasoning
        print("🧠 Brainstorming and creating initial execution plan...")
        if not self.planning_agent:
            raise RuntimeError("Planning agent not initialized. Call create() to instantiate.")
        self.current_plan = await self.planning_agent.create_executable_plan(user_request)
        
        # Save initial plan and reasoning
        await self._save_plan(self.current_plan, version=0)
        print("✅ Initial plan created (see PLAN.md and REASONING.md)")
        
        # Extract tasks
        tasks = self.planning_agent.get_pending_tasks(self.current_plan)
        if not tasks:
            print("⚠️ No tasks found in plan")
            return "Unable to create an execution plan for this request."
        
        print(f"📊 Found {len(tasks)} tasks to execute")
        
        # Execute tasks with dynamic revision
        completed_count = 0
        revision_count = 0
        
        while tasks:
            current_task = tasks[0]
            print(f"\n🔧 Task {current_task}")
            
            try:
                # Execute the task through the graph
                result = await self._execute_task(current_task)
                
                # Update plan status
                self.current_plan = self.planning_agent.update_plan_status(
                    self.current_plan, 
                    current_task
                )
                completed_count += 1
                if self.planning_agent:
                    self.planning_agent.tasks_since_revision += 1
                
                # Get execution memory from the compiled graph
                execution_memory = self.compiled_graph.execution_state

                # Revise the plan
                revised_plan = await self.planning_agent.revise_plan(
                    self.current_plan,
                    execution_memory,
                    self.original_request
                )
                    
                if revised_plan != self.current_plan:
                    revision_count += 1
                    self.current_plan = revised_plan
                        
                # Save revised plan and reasoning
                if save_plan_history:
                    await self._save_plan(self.current_plan, version=revision_count)
                        
                # Re-extract remaining tasks from revised plan
                tasks = self.planning_agent.get_pending_tasks(self.current_plan)
                
            except Exception as e:
                print(f"❌ Task failed: {str(e)}")
                logger.error(f"Task execution failed: {e}", exc_info=True)
                
                # Force plan revision on failure
                print("🔄 Forcing plan revision due to task failure...")
                execution_memory = self.compiled_graph.execution_state
                
                revised_plan = await self.planning_agent.revise_plan(
                    self.current_plan,
                    execution_memory,
                    self.original_request,
                    force=True
                )
                
                if revised_plan != self.current_plan:
                    revision_count += 1
                    self.current_plan = revised_plan
                    await self._save_plan(self.current_plan, version=revision_count)
                    
                # Update remaining tasks
                tasks = self.planning_agent.get_pending_tasks(self.current_plan)
        
        # Generate final response
        print(f"\n📊 Execution complete: {completed_count} tasks completed, {revision_count} revisions")
        
        return result
        
    async def _execute_task(self, task: str) -> str:
        """Execute a single task through the graph"""
        try:
            # Execute through the graph's orchestrator
            result = await self.compiled_graph.execute(
                initial_input=task,
                max_iterations=10  # Limit iterations for safety
            )
            return result
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            raise

    async def _save_plan(self, plan_content: str, version):
        """Save plan to file with version tracking"""
        try:
            # Save current version
            filename = f"{self.plan_file}" if version == "final" else f"PLAN_v{version}.md"
            
            with open(filename, 'w') as f:
                f.write(plan_content)
                
            # Always update the main PLAN.md with latest
            if version != 0:
                with open(self.plan_file, 'w') as f:
                    f.write(plan_content)
                    
        except Exception as e:
            logger.error(f"Failed to save plan: {e}")
