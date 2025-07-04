"""
Memory retrieval agent for intelligent data mapping in multi-step workflows.

This agent uses LLM intelligence to analyze tasks and determine which data
from previous workflow steps should be injected into which tool arguments.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import logging
import os
from dotenv import load_dotenv

from orion.agent_core.agents import build_async_agent
from orion.memory_core.execution_memory.execution_state import ExecutionMemory
from prompts import MEMORY_RETRIEVAL_SYSTEM_PROMPT

load_dotenv()

logger = logging.getLogger(__name__)


class MemoryMapping(BaseModel):
    """Represents a mapping from a workflow node to a specific tool argument."""

    node_name: str = Field(description="The name of the node that provides the data")
    argument_name: str = Field(description="The name of the argument in the tool call that will receive the data")
    description: str = Field(description="A brief description of why this data is relevant to the task")


class MemoryMappings(BaseModel):
    """Represents a list of memory mappings."""

    mappings: List[MemoryMapping] = Field(description="A list of memory mappings")


class MemoryRetrievalAgent:
    """
    LLM-powered agent that intelligently maps workflow data to tool arguments.

    This agent analyzes incoming tasks and determines which data from previous
    workflow steps should be injected into which specific tool arguments.
    """

    def __init__(self):
        """
        Initialize the memory retrieval agent.

        Creates its own LLM agent using environment configuration.
        """
        self.agent = build_async_agent(
            llm_model=os.getenv("GENERAL_MODEL"),  # type: ignore
            base_url=os.getenv("BASE_URL"),  # type: ignore
            api_key=os.getenv("GEMINI_API_KEY"),  # type: ignore
            exponential_backoff_retry=True,
            system_prompt=MEMORY_RETRIEVAL_SYSTEM_PROMPT,
            schema=MemoryMappings,
        )

    async def get_data_mappings(
        self, task: str, target_tool: str, execution_memory: "ExecutionMemory"
    ) -> Optional[Dict[str, str]]:
        """
        Analyze a task and determine which data should be injected into which arguments.

        Args:
            task: The task to be executed
            target_tool: The tool that will execute the task
            execution_memory: Current execution memory state

        Returns:
            List of MemoryMapping objects specifying data injection points
        """
        # Get available data summaries
        available_nodes = execution_memory.get_available_references()

        if not available_nodes:
            return None

        node_summaries = []
        for node_name in available_nodes:
            summary = execution_memory.preview_reference(node_name)
            node_summaries.append(f"- {summary}")

        # Build the analysis prompt
        prompt = self._build_analysis_prompt(task=task, target_tool=target_tool, node_summaries=node_summaries)

        try:
            # Get LLM analysis using the agent
            response = await self.agent(prompt=prompt)

            arguments = {}
            for memory_mapping in response.mappings:
                arguments[memory_mapping.argument_name] = execution_memory.get_node_output(memory_mapping.node_name)

            return arguments

        except Exception as e:
            logger.error(f"Failed to get memory mappings for task '{task}': {e}")

            return None

    def _build_analysis_prompt(self, task: str, target_tool: str, node_summaries: List[str]) -> str:
        """Build the prompt for memory analysis."""
        return f"""TASK TO EXECUTE:
{task}

TARGET TOOL:
{target_tool}

AVAILABLE DATA FROM PREVIOUS STEPS:
{chr(10).join(node_summaries)}

Please analyze this task and return the appropriate data mappings as a JSON array."""
