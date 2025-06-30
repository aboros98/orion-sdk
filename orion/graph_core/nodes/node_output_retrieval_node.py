from .base_node import BaseNode
from orion.agent_core.models import ToolCall
from orion.memory_core.execution_memory.execution_state import ExecutionMemory
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class NodeOutputRetrievalNode(BaseNode):
    """
    A node that retrieves the output of a specified node from execution memory.
    
    This node:
    - Takes a ToolCall as input with 'node_name' in arguments
    - Retrieves the most recent output for that node from execution memory
    - Returns the output if found, or an appropriate message if not found
    """

    def __init__(self, name: str) -> None:
        """
        Initialize a node output retrieval node.

        Args:
            name: Unique identifier for the node.
        """
        # BaseNode requires a callable, but the logic is in compute.
        # So we provide a no-op lambda.
        super().__init__(name, lambda: None)
        self._execution_memory: Optional[ExecutionMemory] = None

    def set_execution_memory(self, execution_memory: ExecutionMemory) -> None:
        """Set the ExecutionMemory instance for this node to read from."""
        self._execution_memory = execution_memory
        logger.debug(f"NodeOutputRetrievalNode '{self.name}' connected to ExecutionMemory")

    async def compute(self, input_data: ToolCall, *args, **kwargs) -> str:
        """
        Retrieve the output of a specified node from execution memory.
        
        Args:
            input_data: A ToolCall object with 'node_name' in its arguments.
        
        Returns:
            The output from the specified node, or an error message if not found.
        
        Raises:
            ValueError: If no execution memory is available or if node name is not provided.
        """
        logger.info(f"NodeOutputRetrievalNode '{self.name}' processing retrieval request")
        
        if not self._execution_memory:
            raise ValueError(f"NodeOutputRetrievalNode '{self.name}' has no execution memory available")

        try:
            # Extract node name from ToolCall arguments
            node_name = input_data.arguments.get('node_name')
            
            if not node_name:
                return "Error: No node name provided. Please specify 'node_name' in the tool call arguments."

            # Retrieve the node output from execution memory
            node_output = self._execution_memory.get_node_output(node_name)
            
            if node_output is not None:
                logger.info(f"NodeOutputRetrievalNode '{self.name}' successfully retrieved output for node '{node_name}'")
                return f"Output from node '{node_name}':\n{node_output}"
            else:
                logger.warning(f"NodeOutputRetrievalNode '{self.name}' could not find output for node '{node_name}'")
                return f"No output found for node '{node_name}'. The node may not have been executed yet or may not exist."

        except Exception as e:
            logger.error(f"NodeOutputRetrievalNode '{self.name}' failed to retrieve node output: {e}")
            raise Exception(f"Node output retrieval failed: {e}") 