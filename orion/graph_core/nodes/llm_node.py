from typing import Callable
from types import AsyncGeneratorType
from .base_node import BaseNode
import logging

logger = logging.getLogger(__name__)


class LLMNode(BaseNode):
    """
    A clean node that processes input through an LLM agent function.
    
    This is the basic LLM node without memory access or orchestrator capabilities.
    For memory access, use MemoryReaderNode. For orchestration, use OrchestratorNode.
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

    async def compute(self, input_data, *args, **kwargs) -> str:
        """
        Execute the LLM agent function with the provided input.
        Returns string response from the LLM.
        """
        try:
            input_context = str(input_data) if input_data is not None else ""
            
            # Execute LLM function
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
