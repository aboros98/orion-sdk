from typing import Callable, Union, List, Optional
from types import AsyncGeneratorType
from .base_node import BaseNode
from orion.agent_core.models import Response, ToolCall
from orion.memory_core.execution_memory.execution_state import ExecutionMemory
import logging

logger = logging.getLogger(__name__)


class MemoryReaderNode(BaseNode):
    """
    Simplified LLM node that can read from ExecutionMemory and provide memory context to the LLM.
    """

    def __init__(
        self, 
        name: str, 
        compute_fn: Callable,
        memory_filter_nodes: Optional[List[str]] = None
    ) -> None:
        """
        Initialize a memory reader node.

        Args:
            name: Unique identifier for the node
            compute_fn: The LLM agent function to execute
            memory_filter_nodes: Optional list of node names to filter memory by.
                                 If None, reads all memory entries.
        """
        super().__init__(name, compute_fn)
        self.is_memory_reader = True
        self.memory_filter_nodes = memory_filter_nodes or []
        self._execution_memory: Optional[ExecutionMemory] = None

    def set_execution_memory(self, execution_memory: ExecutionMemory) -> None:
        """Set the ExecutionMemory instance for this node to read from."""
        self._execution_memory = execution_memory
        logger.debug(f"MemoryReaderNode '{self.name}' connected to ExecutionMemory")

    def get_memory_context(self) -> str:
        """Retrieve memory context based on the configured filter."""
        if not self._execution_memory:
            return "No execution memory available."

        # Get memory entries based on filter
        if self.memory_filter_nodes:
            memory_entries = self._execution_memory.get_entries_for_nodes(self.memory_filter_nodes)
            context_header = f"Memory from nodes {self.memory_filter_nodes}:"
        else:
            memory_entries = self._execution_memory.get_entries_for_nodes(None)  # Get all
            context_header = "Complete execution memory:"

        if not memory_entries:
            return f"{context_header}\nNo memory entries found."

        # Format memory entries simply
        formatted_entries = []
        for entry in memory_entries:
            if entry.node_name not in ["__start__", "__end__"]:
                formatted_entry = f"Node: {entry.node_name}\nOutput: {entry.node_output}\n---"
                formatted_entries.append(formatted_entry)

        if not formatted_entries:
            return f"{context_header}\nNo relevant memory entries found."

        memory_context = f"{context_header}\n\n" + "\n".join(formatted_entries)
        return memory_context

    async def compute(self, input_data, *args, **kwargs) -> Union[str, ToolCall]:
        """Execute the LLM agent function with both input data and memory context."""
        try:
            # Get current input context
            input_context = str(input_data) if input_data is not None else ""
            
            # Get memory context
            memory_context = self.get_memory_context()
            
            # Combine input and memory context
            enhanced_context = f"""Memory context:
{memory_context}

Current input:
{input_context}"""

            logger.debug(f"MemoryReaderNode '{self.name}' providing enhanced context with memory")
            
            # Execute LLM function with enhanced context
            func_output = await self.node_func(prompt=enhanced_context)

            # Handle different output types
            if isinstance(func_output, AsyncGeneratorType):
                full_response = ""
                async for chunk in func_output:
                    print(chunk, end="", flush=True)
                    full_response += chunk
                func_output = full_response
            elif isinstance(func_output, Response):
                func_output = func_output.response

            return func_output

        except Exception as e:
            logger.error(f"MemoryReaderNode '{self.name}' failed to compute: {e}")
            raise Exception(f"Memory-enhanced LLM computation failed: {e}")