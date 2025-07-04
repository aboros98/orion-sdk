from re import A
from typing import Dict, List, Optional, Any
import logging
import time

from .nodes import BaseNode, OrchestratorNode
from .edges import BaseEdge, ConditionalEdge, Edge
from orion.memory_core import ExecutionMemory
from orion.memory_core.memory_retrieval_agent import MemoryRetrievalAgent
from orion.agent_core.models import ToolCall
from orion.agent_core.config import LLMConfig

# Import for type checking
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orion.persistence.event_store import EventStore

logger = logging.getLogger(__name__)


class CompiledGraph:
    """Simplified compiled graph with cycle support."""

    def __init__(
        self,
        nodes: Dict[str, BaseNode],
        edges: Dict[str, List[BaseEdge]],
        orchestrator_nodes: Optional[List[str]] = None,
        event_store: Optional["EventStore"] = None,
        workflow_id: Optional[str] = None,
    ):
        self.nodes = nodes
        self.edges = edges.copy()
        self.orchestrator_nodes = orchestrator_nodes or []
        self.event_store = event_store
        self.memory_retrieval_agent = MemoryRetrievalAgent()
        self.execution_state = ExecutionMemory(event_store=event_store, workflow_id=workflow_id)

        # Convert orchestrator regular edges to conditional edges
        self._create_orchestrator_conditional_edges()

        # Connect orchestrator nodes to execution memory (they still need it for routing decisions)
        self._connect_orchestrators_to_memory()

        logger.info(f"Graph compiled with {len(self.nodes)} nodes, {len(self.orchestrator_nodes)} orchestrators")

    async def execute(
        self,
        initial_input: str,
        max_iterations: int = 100,
        max_execution_time: int = 300,  # 5 minutes
        max_node_retries: int = 3,  # Max retries per node for cycles
    ) -> str:
        """
        Execute the compiled graph with cycle support.

        Args:
            initial_input: Initial input to the graph
            max_iterations: Maximum number of node executions
            max_execution_time: Maximum execution time in seconds
            max_node_retries: Maximum retries per node in cycles
        """
        start_time = time.time()
        execution_count = 0
        node_retry_counts = {}  # Track retries per node
        execution_path = []  # Track execution path

        # Record workflow start event
        if self.event_store:
            try:
                await self.event_store.store_event(
                    workflow_id=self.execution_state.workflow_id,
                    event_type="workflow_started",
                    event_data={
                        "initial_input": initial_input,
                        "max_iterations": max_iterations,
                        "max_execution_time": max_execution_time,
                        "max_node_retries": max_node_retries,
                    },
                )
            except Exception as e:
                logger.error(f"Failed to record workflow start event: {e}")

        logger.info("Starting graph execution with cycle support")

        try:
            # Start with primary orchestrator if exists, otherwise start node
            current_node = self._find_primary_orchestrator() or "__start__"
            current_input = initial_input

            while (
                current_node
                and current_node != "__end__"
                and execution_count < max_iterations
                and time.time() - start_time < max_execution_time
            ):
                # Skip system start node
                if current_node == "__start__":
                    current_node = self._find_next_node(current_node, None)
                    # For nodes connected to __start__, use initial input
                    current_input = initial_input
                    continue

                # Check retry limits for cycles
                if current_node in node_retry_counts:
                    if node_retry_counts[current_node] >= max_node_retries:
                        logger.warning(
                            f"Node {current_node} exceeded retry limit ({max_node_retries}), ending execution"
                        )
                        break
                    logger.debug(f"Retrying node {current_node} (attempt {node_retry_counts[current_node] + 1})")

                logger.debug(f"Executing node: {current_node}")

                # Add to execution path
                execution_path.append(current_node)

                result = await self.nodes[current_node].compute(current_input)

                # Store result in memory UNLESS the node is an orchestrator (orchestrators are read-only)
                if not isinstance(self.nodes[current_node], OrchestratorNode):
                    # Determine node type based on class name
                    node_type = self._get_node_type(self.nodes[current_node])
                    self.execution_state.add_exec_step(
                        current_node, current_input, result, solved_task=initial_input, node_type=node_type
                    )
                else:
                    logger.debug(f"Skipping memory write for orchestrator node '{current_node}'")
                execution_count += 1

                node_retry_counts[current_node] = node_retry_counts.get(current_node, 0) + 1

                logger.debug(f"Node {current_node} completed. Result type: {type(result)}")

                # Find next node based on current node and result
                next_node = self._find_next_node(current_node, result)
                logger.debug(f"Next node: {next_node}")

                # Handle cycles - if next node was already executed, it's a cycle
                if next_node and next_node in node_retry_counts and next_node != "__end__":
                    logger.info(f"Detected cycle: {current_node} -> {next_node}")

                # Prepare input for next iteration - with memory retrieval integration
                current_input = await self._prepare_next_input(current_node, result, next_node, str(current_input))
                current_node = next_node

            # Check if any nodes were executed
            if execution_count == 0:
                logger.warning("No nodes were executed")
                return "No nodes executed - check your graph structure and connections"

            # Get final output from the last node in execution path
            if execution_path:
                final_node = execution_path[-1]
                final_output = self.execution_state.get_node_output(final_node)
                logger.info(f"Final output from node '{final_node}': {type(final_output)}")
            else:
                final_output = "No execution path recorded"

            # Record workflow completion
            if self.event_store:
                try:
                    await self.event_store.store_event(
                        workflow_id=self.execution_state.workflow_id,
                        event_type="workflow_completed",
                        event_data={
                            "final_output": final_output,
                            "total_iterations": execution_count,
                            "execution_time": time.time() - start_time,
                            "node_retry_counts": node_retry_counts,
                            "execution_path": execution_path,
                        },
                    )
                except Exception as e:
                    logger.error(f"Failed to record workflow completion: {e}")

            logger.info(f"Graph execution completed after {execution_count} iterations")
            logger.info(f"Execution path: {' -> '.join(execution_path)}")
            logger.info(f"Node retry counts: {node_retry_counts}")
            return final_output or "No output generated"

        except Exception as e:
            logger.error(f"Graph execution failed: {e}")

            # Record workflow failure
            if self.event_store:
                try:
                    await self.event_store.store_event(
                        workflow_id=self.execution_state.workflow_id,
                        event_type="workflow_failed",
                        event_data={
                            "error": str(e),
                            "node_retry_counts": node_retry_counts,
                            "execution_path": execution_path,
                        },
                    )
                except Exception as store_error:
                    logger.error(f"Failed to record workflow failure: {store_error}")

            raise

    def _find_primary_orchestrator(self) -> Optional[str]:
        """Find the primary orchestrator (the one connected to __start__)."""
        if "__start__" in self.edges:
            for edge in self.edges["__start__"]:
                if isinstance(edge, Edge) and edge.target in self.orchestrator_nodes:
                    return edge.target
        return None

    def _find_next_node(self, current_node: str, result) -> Optional[str]:
        """Find the next node to execute based on current node and its result."""
        # Check if current node has outgoing edges
        if current_node not in self.edges:
            logger.debug(f"No edges from {current_node}, ending execution")
            return "__end__"

        edges = self.edges[current_node]
        if not edges:
            logger.debug(f"No edges from {current_node}, ending execution")
            return "__end__"

        # Handle edges (usually just one edge per node)
        for edge in edges:
            if isinstance(edge, Edge):
                logger.debug(f"Following direct edge from {current_node} to {edge.target}")
                return edge.target
            elif isinstance(edge, ConditionalEdge):
                try:
                    next_node = edge.evaluate_condition(self.nodes[current_node], result)
                    logger.debug(f"Conditional edge from {current_node} routed to {next_node}")
                    return next_node
                except Exception as e:
                    logger.error(f"Failed to evaluate conditional edge from {current_node}: {e}")
                    return "__end__"

        logger.debug(f"No valid edges from {current_node}, ending execution")
        return "__end__"

    async def _prepare_next_input(
        self, current_node: str, result: Any, next_node: Optional[str], original_task: str
    ) -> Any:
        """
        Prepare input for the next node with memory retrieval integration.

        If the current node is an orchestrator and returned a ToolCall,
        enhance the ToolCall with memory retrieval before passing to next node.
        """
        # If current node is not an orchestrator, pass result as-is
        if not isinstance(self.nodes[current_node], OrchestratorNode):
            return result

        # If result is not a ToolCall, pass as-is
        if not isinstance(result, ToolCall):
            return result

        try:
            # Use memory retrieval agent to get data mappings
            logger.debug(f"Getting memory mappings for task: {original_task}, target tool: {result.tool_name}")

            if "_needs_memory" in result.arguments and result.arguments["_needs_memory"]:
                func_arguments = await self.memory_retrieval_agent.get_data_mappings(
                    task=original_task, target_tool=result.tool_name, execution_memory=self.execution_state
                )
                if func_arguments:
                    result.arguments = func_arguments

            return result

        except Exception as e:
            logger.error(f"Failed to enhance ToolCall with memory retrieval: {e}")
            return result  # Fallback to original ToolCall

    def _create_orchestrator_conditional_edges(self):
        """Convert regular edges from all orchestrators to conditional edges."""
        if not self.orchestrator_nodes:
            logger.debug("No orchestrators found, skipping conditional edge creation")
            return

        for orchestrator_name in self.orchestrator_nodes:
            # Find all target nodes from this orchestrator's regular edges
            target_nodes = []
            if orchestrator_name in self.edges:
                for edge in self.edges[orchestrator_name]:
                    if isinstance(edge, Edge):
                        target_nodes.append(edge.target)

            if not target_nodes:
                logger.debug(f"No edges from orchestrator {orchestrator_name} to convert")
                continue

            # Create condition mapping (tool_name -> node_name)
            condition_mapping = {node_name: node_name for node_name in target_nodes}

            # Create orchestrator routing condition function
            def orchestrator_routing_condition(node_output) -> str:
                """Route based on the tool_name from the orchestrator's ToolCall output."""
                if isinstance(node_output, ToolCall):
                    return node_output.tool_name
                else:
                    # Fallback: try to parse as string or return first available node
                    if target_nodes:
                        logger.warning(
                            f"Orchestrator output is not ToolCall, routing to first available node: {target_nodes[0]}"
                        )
                        return target_nodes[0]
                    else:
                        raise ValueError("No target nodes available for routing")

            # Replace regular edges with conditional edge
            self.edges[orchestrator_name] = [
                ConditionalEdge(orchestrator_name, orchestrator_routing_condition, condition_mapping)
            ]

            logger.info(f"Created conditional edges from orchestrator {orchestrator_name} to: {target_nodes}")

    def _connect_orchestrators_to_memory(self):
        """Connect orchestrator nodes to ExecutionMemory (they need it for routing decisions)."""
        for node_name, node in self.nodes.items():
            if isinstance(node, OrchestratorNode) and hasattr(node, "set_execution_memory"):
                node.set_execution_memory(self.execution_state)  # type: ignore
                logger.debug(f"Connected orchestrator '{node_name}' to ExecutionMemory")

    def visualize(self) -> str:
        """Return a string visualization of the compiled graph."""
        lines = ["Compiled Graph Visualization:"]
        lines.append("=" * 40)

        lines.append(f"\nNodes ({len(self.nodes)}):")
        for name, node in self.nodes.items():
            node_type = type(node).__name__
            if isinstance(node, OrchestratorNode):
                lines.append(f"  {name} ({node_type}) [ORCHESTRATOR]")
            else:
                lines.append(f"  {name} ({node_type})")

        if self.orchestrator_nodes:
            lines.append(f"\nOrchestrators: {self.orchestrator_nodes}")

        lines.append(f"\nEdges:")
        for source, edge_list in self.edges.items():
            for edge in edge_list:
                if isinstance(edge, Edge):
                    lines.append(f"  {source} -> {edge.target}")
                elif isinstance(edge, ConditionalEdge):
                    targets = list(edge.condition_mapping.values())
                    lines.append(f"  {source} -> {targets} [CONDITIONAL]")

        return "\n".join(lines)

    def _get_node_type(self, node: BaseNode) -> str:
        """Helper method to determine the node type based on its class name."""
        return str(type(node).__name__)
