from typing import Callable, Optional, Any, Dict, List, TYPE_CHECKING
from .base_node import BaseNode
from ..compiled_graph import CompiledGraph
import logging
import time

if TYPE_CHECKING:
    from ..workflow import WorkflowGraph

logger = logging.getLogger(__name__)


class LoopNode(BaseNode):
    """
    A node that contains and repeatedly executes a sub-graph.

    The LoopNode acts as a while loop - it executes its sub-graph repeatedly
    until the loop condition returns False or max iterations is reached.

    Example usage:
        # Create sub-graph: b1 -> b2
        sub_graph = WorkflowGraph()
        sub_graph.add_node("b1", processor_function)
        sub_graph.add_node("b2", analyzer_function)
        sub_graph.add_edge("__start__", "b1")
        sub_graph.add_edge("b1", "b2")
        sub_graph.add_edge("b2", "__end__")

        # Create loop condition
        def should_continue(output, iteration_count):
            return iteration_count < 5 and "continue" in output.lower()

        # Create loop node
        loop_node = LoopNode("loop", sub_graph, should_continue)
    """

    def __init__(
        self,
        name: str,
        sub_graph: "WorkflowGraph",
        loop_condition: Callable[[str, int], bool],
        max_iterations: int = 100,
        max_execution_time: int = 300,  # 5 minutes per loop execution
    ) -> None:
        """
        Initialize a loop node.

        Args:
            name: Unique identifier for the node
            sub_graph: The WorkflowGraph to execute repeatedly
            loop_condition: Function that receives (output, iteration_count) and returns bool
                          Returns True to continue looping, False to exit
            max_iterations: Maximum number of loop iterations
            max_execution_time: Maximum execution time per sub-graph execution in seconds

        Raises:
            ValueError: If name is empty, sub_graph is not a WorkflowGraph, or loop_condition is not callable
        """
        # Use a dummy function for BaseNode compatibility
        super().__init__(name, lambda x: x)

        # Check if sub_graph has the expected WorkflowGraph interface
        if not hasattr(sub_graph, "nodes") or not hasattr(sub_graph, "edges") or not hasattr(sub_graph, "compile"):
            raise ValueError("sub_graph must be a WorkflowGraph instance")
        if not callable(loop_condition):
            raise ValueError("loop_condition must be callable")
        if max_iterations <= 0:
            raise ValueError("max_iterations must be positive")
        if max_execution_time <= 0:
            raise ValueError("max_execution_time must be positive")

        self.sub_graph = sub_graph
        self.loop_condition = loop_condition
        self.max_iterations = max_iterations
        self.max_execution_time = max_execution_time
        self._compiled_sub_graph: Optional[CompiledGraph] = None

        logger.info(f"LoopNode '{name}' created with max_iterations={max_iterations}")

    def _compile_sub_graph(self) -> CompiledGraph:
        """Compile the sub-graph for execution once and reuse."""
        if self._compiled_sub_graph is None:
            self._compiled_sub_graph = self.sub_graph.compile()
            logger.debug(f"LoopNode '{self.name}' compiled sub-graph (one-time)")
        return self._compiled_sub_graph

    async def compute(self, input_data, *args, **kwargs) -> str:
        """
        Execute the loop by repeatedly running the sub-graph.

        Args:
            input_data: Initial input to the first iteration of the sub-graph

        Returns:
            str: The final output from the last iteration

        Raises:
            Exception: If loop execution fails
        """
        try:
            compiled_sub_graph = self._compile_sub_graph()

            current_input = str(input_data) if input_data is not None else ""
            iteration_count = 0
            loop_start_time = time.time()

            logger.info(
                f"LoopNode '{self.name}' starting execution (reusing compiled sub-graph) with input: {current_input[:100]}..."
            )

            while iteration_count < self.max_iterations:
                iteration_count += 1
                iteration_start_time = time.time()

                logger.debug(f"LoopNode '{self.name}' iteration {iteration_count}/{self.max_iterations}")

                # Execute sub-graph for this iteration
                try:
                    # Keep execution memory for history - the fixed get_node_output() will return latest
                    logger.debug(f"LoopNode '{self.name}' iteration {iteration_count} input: {current_input}")

                    iteration_output = await compiled_sub_graph.execute(
                        initial_input=current_input, max_execution_time=self.max_execution_time
                    )
                    logger.debug(f"LoopNode '{self.name}' iteration {iteration_count} output: {iteration_output}")
                except Exception as e:
                    logger.error(f"LoopNode '{self.name}' iteration {iteration_count} failed: {e}")
                    raise Exception(f"Loop iteration {iteration_count} failed: {e}")

                iteration_time = time.time() - iteration_start_time
                logger.debug(f"LoopNode '{self.name}' iteration {iteration_count} completed in {iteration_time:.2f}s")

                # Check loop condition
                try:
                    logger.debug(f"LoopNode '{self.name}' calling loop condition with output: {iteration_output}")
                    should_continue = self.loop_condition(iteration_output, iteration_count)
                    logger.debug(f"LoopNode '{self.name}' loop condition returned: {should_continue}")
                except Exception as e:
                    logger.error(f"LoopNode '{self.name}' loop condition failed: {e}")
                    should_continue = False

                if not should_continue:
                    logger.info(
                        f"LoopNode '{self.name}' loop condition returned False, exiting after {iteration_count} iterations"
                    )
                    return iteration_output

                # Prepare input for next iteration (current output becomes next input)
                current_input = iteration_output

                # Check total loop time
                total_loop_time = time.time() - loop_start_time
                if total_loop_time > (self.max_execution_time * self.max_iterations):
                    logger.warning(f"LoopNode '{self.name}' exceeded total execution time, breaking loop")
                    return iteration_output

            # Reached max iterations
            logger.warning(f"LoopNode '{self.name}' reached max iterations ({self.max_iterations}), ending loop")
            return current_input

        except Exception as e:
            logger.error(f"LoopNode '{self.name}' failed: {e}")
            raise Exception(f"LoopNode execution failed: {e}")

    def get_sub_graph_info(self) -> Dict[str, Any]:
        """Get information about the sub-graph for debugging/visualization."""
        return {
            "sub_graph_nodes": list(self.sub_graph.nodes.keys()),
            "sub_graph_edges": {
                source: [f"{edge.source}->{edge.target}" if hasattr(edge, "target") else str(edge) for edge in edges]
                for source, edges in self.sub_graph.edges.items()
            },
            "max_iterations": self.max_iterations,
            "max_execution_time": self.max_execution_time,
        }

    def get_loop_execution_history(self) -> List[Dict[str, Any]]:
        """
        Get the execution history of all loop iterations.

        Returns:
            List of dictionaries containing execution steps for each iteration.
            Each dict has node_name, node_input, node_output, and iteration info.
        """
        if not self._compiled_sub_graph:
            return []

        execution_steps = self._compiled_sub_graph.execution_state._exec_steps

        # Group execution steps by iteration (rough estimation based on order)
        history = []
        for step in execution_steps:
            history.append(
                {
                    "node_name": step.node_name,
                    "node_input": str(step.node_input),
                    "node_output": step.node_output,
                    "step_index": len(history),
                }
            )

        return history

    def __str__(self) -> str:
        return f"LoopNode(name={self.name}, sub_graph_nodes={len(self.sub_graph.nodes)}, max_iterations={self.max_iterations})"

    def __repr__(self) -> str:
        return self.__str__()
