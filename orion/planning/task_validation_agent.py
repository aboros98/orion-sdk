import os
from typing import Optional, Callable
from dotenv import load_dotenv
from orion.agent_core.agents import build_async_agent
from prompts import TASK_VALIDATION_SYSTEM_PROMPT
from .planning_models import TaskValidationResult

load_dotenv()


class TaskValidationAgent:
    """
    Lightweight task validation agent that assesses whether individual tasks
    have been successfully completed by analyzing task objectives against actual outputs.
    """
    
    validation_agent: Optional[Callable]
    
    def __init__(self):
        """Initialize the task validation agent."""
        self.validation_agent = None
    
    @classmethod
    async def create(cls):
        """
        Create and initialize a TaskValidationAgent instance.
        
        This factory method handles the async initialization of the agent.
        """
        instance = cls()
        instance.validation_agent = instance._create_validation_agent()

        return instance
    
    def _create_validation_agent(self):
        """Create the task validation LLM agent."""
        return build_async_agent(
            api_key=os.getenv("GEMINI_API_KEY"), #type: ignore
            base_url=os.getenv("BASE_URL"), #type: ignore
            llm_model=os.getenv("PLANNING_MODEL"), #type: ignore  # Using same lightweight model as planning
            system_prompt=TASK_VALIDATION_SYSTEM_PROMPT,
            schema=TaskValidationResult,
            exponential_backoff_retry=True
        )
    
    async def validate_task(self, current_task: str, actual_output: str) -> TaskValidationResult:
        """
        Validate whether a task has been completed successfully.
        
        Args:
            current_task: The task description with its intended objective
            actual_output: The detailed execution results from the node
            
        Returns:
            TaskValidationResult containing status, reasoning, and workflow impact
        """
        if not self.validation_agent:
            raise RuntimeError("Validation agent not initialized. Call `create` to instantiate.")

        prompt = f"""CURRENT TASK:
{current_task}

ACTUAL OUTPUT:
{actual_output}

Please assess whether this task has been completed successfully."""
        
        response = await self.validation_agent(prompt=prompt)

        return response
