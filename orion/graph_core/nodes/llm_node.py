from typing import Callable, Union, List, Optional
from types import AsyncGeneratorType
from .base_node import BaseNode
from orion.agent_core.models import ToolCall
from orion.memory_core.execution_memory.execution_state import ExecutionMemory
import logging

logger = logging.getLogger(__name__)


class LLMNode(BaseNode):
    """
    A node that processes input through an LLM agent function.
    
    Can optionally read from ExecutionMemory to provide enhanced context.
    """

    def __init__(
        self, 
        name: str, 
        compute_fn: Callable,
        memory_filter_nodes: Optional[List[str]] = None,
        _enable_memory: bool = False
    ) -> None:
        """
        Initialize an LLM node.

        Args:
            name: Unique identifier for the node
            compute_fn: The LLM agent function to execute
            memory_filter_nodes: Optional list of node names to filter memory by.
                                 If None and memory is enabled, reads all memory entries.
            _enable_memory: Private parameter to enable memory reading functionality

        Raises:
            ValueError: If name is empty or compute_fn is not callable
        """
        super().__init__(name, compute_fn)
        self._enable_memory = _enable_memory
        self.memory_filter_nodes = memory_filter_nodes or []
        self._execution_memory: Optional[ExecutionMemory] = None
        
        # Set memory reader flag for backward compatibility
        if self._enable_memory:
            self.is_memory_reader = True

    def set_execution_memory(self, execution_memory: ExecutionMemory) -> None:
        """Set the ExecutionMemory instance for this node to read from."""
        if self._enable_memory:
            self._execution_memory = execution_memory
            logger.debug(f"LLMNode '{self.name}' connected to ExecutionMemory")

    def get_memory_context(self) -> str:
        """Retrieve memory context based on the configured filter."""
        if not self._enable_memory or not self._execution_memory:
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
        """
        Execute the LLM agent function with the provided input.
        If memory is enabled, enhances context with memory data.
        Returns string response from the LLM.
        """
        try:
            input_context = str(input_data) if input_data is not None else ""
            
            # Enhance with memory context if enabled
            if self._enable_memory:
                memory_context = self.get_memory_context()
                enhanced_context = f"""Memory context:
{memory_context}

Current input:
{input_context}"""
                logger.debug(f"LLMNode '{self.name}' providing enhanced context with memory")
                final_context = enhanced_context
            else:
                final_context = input_context
            
            # Execute LLM function
            func_output = await self.node_func(prompt=final_context)

            # Handle different output types
            if isinstance(func_output, AsyncGeneratorType):
                full_response = ""
                async for chunk in func_output:
                    print(chunk, end="", flush=True)
                    full_response += chunk

                func_output = full_response

            return func_output

        except Exception as e:
            error_msg = f"LLM computation failed: {e}"
            if self._enable_memory:
                error_msg = f"Memory-enhanced {error_msg}"
            logger.error(f"LLMNode '{self.name}' failed to compute: {e}")
            raise Exception(error_msg)
