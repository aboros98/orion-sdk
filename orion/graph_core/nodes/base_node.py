from typing import Callable, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseNode(ABC):
    """
    Abstract base class for all nodes in the execution graph.

    Simple rules:
    - If chained: get last output from previous node
    - If connected to exec memory: write there
    """

    @abstractmethod
    def __init__(self, name: str, node_func: Callable) -> None:
        """
        Initialize a base node.

        Args:
            name: Unique identifier for the node
            node_func: The function to execute when the node is processed

        Raises:
            ValueError: If name is empty or node_func is not callable
        """
        if not name or not name.strip():
            raise ValueError("Node name cannot be empty")
        if not callable(node_func):
            raise ValueError("node_func must be callable")

        self.name = name
        self.is_orchestrator = False

        self.node_func = node_func

    @abstractmethod
    async def compute(self, input_data, *args, **kwargs) -> Any:
        """
        Execute the node's computation function.

        Args:
            input_data: The input data from the previous node
            *args, **kwargs: Additional arguments

        Returns:
            Any: The output data from the computation

        Raises:
            Exception: If the computation fails
        """
        pass
