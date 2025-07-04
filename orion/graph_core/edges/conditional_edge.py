from typing import Callable, Any, Dict
from ..nodes import BaseNode
from .base_edge import BaseEdge
import logging

logger = logging.getLogger(__name__)


class ConditionalEdge(BaseEdge):
    """
    Simplified conditional edge that routes based on node output.
    """

    def __init__(
        self,
        source: str,
        condition: Callable,
        condition_mapping: Dict[str, str],
    ) -> None:
        """
        Initialize a conditional edge.

        Args:
            source: The name of the source node
            condition: A function that takes node_output and returns a condition result
            condition_mapping: Dictionary mapping condition results to target node names
        """
        super().__init__(source)
        if not callable(condition):
            raise ValueError("Condition must be callable")
        if not condition_mapping:
            raise ValueError("Condition mapping cannot be empty")
        if not all(isinstance(k, str) and isinstance(v, str) for k, v in condition_mapping.items()):
            raise ValueError("Condition mapping must contain string keys and values")
        if not all(k.strip() and v.strip() for k, v in condition_mapping.items()):
            raise ValueError("Condition mapping keys and values cannot be empty")

        self.condition = condition
        self.condition_mapping = condition_mapping

    def evaluate_condition(self, node: BaseNode, node_output: Any) -> str:
        """
        Evaluate the condition and return the target node name.

        Args:
            node: The current node (must match the source)
            node_output: The output from the current node

        Returns:
            str: The name of the next node to execute

        Raises:
            ValueError: If condition result not in mapping
            Exception: If the condition function fails
        """
        if self.source != node.name:
            raise ValueError(f"ConditionalEdge source '{self.source}' does not match node '{node.name}'")

        try:
            # Evaluate condition with just the node output
            condition_result = self.condition(node_output)

            logger.debug(f"ConditionalEdge evaluated condition for node '{node.name}': {condition_result}")

        except Exception as e:
            logger.error(f"ConditionalEdge condition evaluation failed for node '{node.name}': {e}")
            raise Exception(f"Condition evaluation failed: {e}")

        if condition_result not in self.condition_mapping:
            available_results = list(self.condition_mapping.keys())
            raise ValueError(
                f"Condition result '{condition_result}' not found in mapping for edge from '{self.source}'. "
                f"Available results: {available_results}"
            )

        next_node = self.condition_mapping[condition_result]
        logger.debug(
            f"ConditionalEdge routing from '{self.source}' to '{next_node}' based on result '{condition_result}'"
        )
        return next_node

    # Keep old method for backwards compatibility
    def get_next_node(self, node: BaseNode, execution_state=None) -> str:
        """Legacy method - get node output from execution state and evaluate."""
        if execution_state:
            node_output = execution_state.get_node_output(node.name)
            return self.evaluate_condition(node, node_output)
        else:
            raise ValueError("execution_state required for get_next_node method")

    def __str__(self) -> str:
        return f"ConditionalEdge(source={self.source}, condition_mapping={self.condition_mapping})"

    def __repr__(self) -> str:
        return self.__str__()
