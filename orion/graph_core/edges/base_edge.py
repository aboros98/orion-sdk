from ..nodes import BaseNode
from abc import ABC, abstractmethod
from typing import Optional


class BaseEdge(ABC):
    """
    Abstract base class for all edges in the execution graph.

    An edge defines how to transition from one node to another based on
    the output of the current node.

    Attributes:
        source: The name of the source node
    """

    def __init__(self, source: str, target: Optional[str] = None) -> None:
        """
        Initialize a base edge.

        Args:
            source: The name of the source node

        Raises:
            ValueError: If source is empty
        """
        if not source or not source.strip():
            raise ValueError("Source node name cannot be empty")

        self.source = source
        self.target = target

    @abstractmethod
    def get_next_node(self, node: BaseNode) -> str:
        """
        Determine the next node in the graph based on the output of the current node.

        Args:
            node: The current node that has just been executed

        Returns:
            str: The name of the next node to execute

        Raises:
            ValueError: If the edge logic cannot determine the next node
        """
        pass
