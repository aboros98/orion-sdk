from ..nodes import BaseNode
from .base_edge import BaseEdge


class Edge(BaseEdge):
    """
    A simple, direct edge between two nodes.

    This edge type always transitions to the same target node regardless
    of the source node's output.
    """

    def __init__(self, source: str, target: str) -> None:
        """
        Initialize a direct edge.

        Args:
            source: The name of the source node
            target: The name of the target node

        Raises:
            ValueError: If source or target is empty
        """
        super().__init__(source)
        if not target or not target.strip():
            raise ValueError("Target node name cannot be empty")

        self.target = target

    def get_next_node(self, node: BaseNode) -> str:
        """
        Get the target node for this direct edge.

        Args:
            node: The current node (must match the source)

        Returns:
            str: The target node name

        Raises:
            ValueError: If the current node doesn't match the source
        """
        if self.source != node.name:
            raise ValueError(f"Edge {self} does not start from node {node.name}")

        return self.target

    def __str__(self) -> str:
        return f"Edge(source={self.source}, target={self.target})"

    def __repr__(self) -> str:
        return self.__str__()
