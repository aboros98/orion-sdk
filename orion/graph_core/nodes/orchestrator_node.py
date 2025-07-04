from typing import Callable, Union
from .base_node import BaseNode
from orion.agent_core.models import ToolCall
import logging

logger = logging.getLogger(__name__)


class OrchestratorNode(BaseNode):
    """
    Simplified orchestrator node for workflow routing with memory access.

    The orchestrator:
    - Receives input and decides which node to route to
    - Has access to execution memory for routing decisions
    - Returns ToolCall objects for conditional routing
    """

    def __init__(self, name: str, compute_fn: Callable) -> None:
        """
        Initialize an orchestrator node.

        Args:
            name: Unique identifier for the node
            compute_fn: The orchestrator function that returns ToolCall objects
        """
        super().__init__(name, compute_fn)
        self.is_orchestrator = True
        self.execution_memory = None

    def set_execution_memory(self, execution_memory) -> None:
        """Set the execution memory for this orchestrator."""
        self.execution_memory = execution_memory
        logger.debug(f"Orchestrator '{self.name}' connected to ExecutionMemory")

    def get_memory_context(self) -> str:
        """Get simple memory context for routing decisions."""
        if not self.execution_memory:
            return "No execution history available."

        # Get all execution entries
        entries = self.execution_memory.get_entries_for_nodes()

        if not entries:
            return "No execution history available."

        # Filter out system nodes and format simply
        meaningful_entries = []
        for entry in entries:
            if entry.node_name not in ["__start__", "__end__"]:
                meaningful_entries.append(f"- {entry.node_name}: {entry.node_output}")

        if not meaningful_entries:
            return "No execution history available."

        return "Previous execution history:\n" + "\n".join(meaningful_entries)

    async def compute(self, input_data, *args, **kwargs) -> Union[str, ToolCall]:
        """
        Execute the orchestrator function for task routing.
        Returns ToolCall object for routing decisions.
        """
        try:
            assert self.execution_memory is not None, "Execution memory is not set"

            input_context = str(input_data) if input_data is not None else ""
            memory_summary = self.execution_memory.get_summary_for_orchestrator()

            # Build enhanced context for orchestrator
            enhanced_context = f"""{memory_summary}
            
Task: {input_context}

Route this task to the appropriate tool."""

            logger.debug(f"Orchestrator '{self.name}' processing: {enhanced_context[:200]}...")

            # Execute orchestrator function
            func_output = await self.node_func(prompt=enhanced_context)
            print("-" * 100)
            print(f"Orchestrator '{self.name}' output: {func_output}")
            print("-" * 100)
            # Ensure we return a ToolCall object
            if isinstance(func_output, ToolCall):
                logger.debug(f"Orchestrator routing to: {func_output.tool_name}")
                return func_output
            else:
                # Handle string outputs as feedback/reasoning
                if isinstance(func_output, str):
                    # String outputs are treated as feedback that should trigger plan revision
                    return func_output
                else:
                    # Fallback if orchestrator doesn't return ToolCall or string
                    logger.warning(f"Orchestrator '{self.name}' returned {type(func_output)} instead of ToolCall")
                    return ToolCall(tool_name="default", arguments={"input": str(func_output)})

        except Exception as e:
            logger.error(f"OrchestratorNode '{self.name}' failed to compute: {e}")
            raise Exception(f"Orchestrator computation failed: {e}")
