from typing import Callable, Union
from types import AsyncGeneratorType
from .base_node import BaseNode
from orion.agent_core.models import ToolCall
import logging

logger = logging.getLogger(__name__)


class LLMNode(BaseNode):
    """
    A node that processes input through an LLM agent function.
    
    Data from previous steps is automatically injected via MemoryRetrievalAgent,
    so no manual memory management is needed.
    """

    def __init__(self, name: str, compute_fn: Callable) -> None:
        """
        Initialize an LLM node.

        Args:
            name: Unique identifier for the node
            compute_fn: The LLM agent function to execute

        Raises:
            ValueError: If name is empty or compute_fn is not callable
        """
        super().__init__(name, compute_fn)

    async def compute(self, input_data, *args, **kwargs) -> Union[str, ToolCall]:
        """
        Execute the LLM agent function with the provided input.
        
        All necessary data is provided via input_data arguments,
        automatically injected by MemoryRetrievalAgent.
        """
        if isinstance(input_data, ToolCall):
            input_data = input_data.arguments

        try:
            input_context = str(input_data) if input_data is not None else ""

            # Execute LLM function - data already injected via arguments
            func_output = await self.node_func(prompt=input_context)

            # Handle different output types
            if isinstance(func_output, AsyncGeneratorType):
                full_response = ""
                async for chunk in func_output:
                    print(chunk, end="", flush=True)
                    full_response += chunk

                func_output = full_response

            return func_output

        except Exception as e:
            logger.error(f"LLMNode '{self.name}' failed to compute: {e}")
            raise Exception(f"LLM computation failed: {e}")
