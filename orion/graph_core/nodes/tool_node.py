from typing import Callable
from orion.agent_core.models import ToolCall
from .base_node import BaseNode
import logging
import inspect

logger = logging.getLogger(__name__)


class ToolNode(BaseNode):
    """
    A node that executes tool functions.
    
    Simple behavior:
    - Gets input from previous node or memory
    - Executes tool function
    - Writes to memory if it's chain end or standalone
    """

    def __init__(self, name: str, compute_fn: Callable) -> None:
        """
        Initialize a tool node.

        Args:
            name: Unique identifier for the node
            compute_fn: The tool function to execute

        Raises:
            ValueError: If name is empty or compute_fn is not callable
        """
        super().__init__(name, compute_fn)
        self._failed = False

    async def compute(self, input_data, *args, **kwargs) -> str:
        """
        Execute the tool function with the provided input.
        """
        try:
            if input_data is None:
                logger.warning(f"ToolNode '{self.name}' received no input")
                return "No input provided"

            # Execute tool function - expect ToolCall input
            try:
                if isinstance(input_data, ToolCall):
                    if "_needs_memory" in input_data.arguments:
                        input_data.arguments.pop("_needs_memory")

                    # Use ToolCall arguments
                    result = self.node_func(**input_data.arguments)
                else:
                    # Fallback for string input
                    result = self.node_func(input_data)
                
                # Handle async functions
                if inspect.iscoroutine(result):
                    result = await result

            except Exception as e:
                result = f"Tool execution failed: {str(e)}"
                self._failed = True

            return str(result)

        except Exception as e:
            logger.error(f"ToolNode '{self.name}' failed: {e}")
            raise
