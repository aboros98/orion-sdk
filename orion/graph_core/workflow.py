from .nodes import LLMNode, BaseNode, ToolNode, MemoryReaderNode, OrchestratorNode, LoopNode, HumanInTheLoopNode
from .edges import Edge, ConditionalEdge, BaseEdge
from typing import Any, Callable, Dict, Optional, List, Union
import logging
from .compiled_graph import CompiledGraph
from orion.agent_core.models import ToolCall

logger = logging.getLogger(__name__)


class WorkflowGraph:
    """
    A simplified directed graph for executing computational workflows.
    """

    def __init__(self) -> None:
        """Initialize an empty execution graph."""
        self.nodes: Dict[str, BaseNode] = {}
        self.edges: Dict[str, List[BaseEdge]] = {}
        self.orchestrator_nodes: List[str] = []  # Support multiple orchestrators

        # create start and end nodes
        self.add_node("__start__", lambda x, y: x)
        self.add_node("__end__", lambda x, y: x)

    def add_node(self, node_name: str, node_function: Callable) -> None:
        """Add a node to the execution graph."""
        if not node_name or not node_name.strip():
            raise ValueError("Node name cannot be empty")
        if node_name in self.nodes:
            raise KeyError(f"Node '{node_name}' already exists in the graph")

        if hasattr(node_function, "_is_tool"):
            self.nodes[node_name] = ToolNode(node_name, node_function)
        else:
            self.nodes[node_name] = LLMNode(node_name, node_function)

    def add_orchestrator_node(self, node_name: str, orchestrator_function: Callable) -> None:
        """Add an orchestrator node. Connect manually to __start__ to make it primary."""
        if not node_name or not node_name.strip():
            raise ValueError("Node name cannot be empty")
        if node_name in self.nodes:
            raise KeyError(f"Node '{node_name}' already exists in the graph")
        if not callable(orchestrator_function):
            raise ValueError("orchestrator_function must be callable")

        # Create orchestrator node
        orchestrator = OrchestratorNode(node_name, orchestrator_function)
        self.nodes[node_name] = orchestrator
        self.orchestrator_nodes.append(node_name)
        
        logger.info(f"Orchestrator '{node_name}' added (connect manually to __start__ to make it primary)")

    def add_memory_reader_node(
        self, 
        node_name: str, 
        llm_function: Callable,
        memory_filter_nodes: Optional[List[str]] = None
    ) -> None:
        """Add a memory reader node that can access ExecutionMemory."""
        if not node_name or not node_name.strip():
            raise ValueError("Node name cannot be empty")
        if node_name in self.nodes:
            raise KeyError(f"Node '{node_name}' already exists in the graph")
        if not callable(llm_function):
            raise ValueError("llm_function must be callable")

        memory_reader = MemoryReaderNode(node_name, llm_function, memory_filter_nodes)
        self.nodes[node_name] = memory_reader
        
        logger.info(f"Memory reader node '{node_name}' added with filter: {memory_filter_nodes or 'all nodes'}")

    def add_loop_node(
        self,
        node_name: str,
        sub_graph: "WorkflowGraph",
        loop_condition: Callable[[str, int], bool],
        max_iterations: int = 100,
        max_execution_time: int = 300
    ) -> None:
        """
        Add a loop node that contains and repeatedly executes a sub-graph.
        
        Args:
            node_name: Unique identifier for the loop node
            sub_graph: The WorkflowGraph to execute repeatedly
            loop_condition: Function that receives (output, iteration_count) and returns bool
                          Returns True to continue looping, False to exit
            max_iterations: Maximum number of loop iterations
            max_execution_time: Maximum execution time per sub-graph execution in seconds
        """
        if not node_name or not node_name.strip():
            raise ValueError("Node name cannot be empty")
        if node_name in self.nodes:
            raise KeyError(f"Node '{node_name}' already exists in the graph")
        if not isinstance(sub_graph, WorkflowGraph):
            raise ValueError("sub_graph must be a WorkflowGraph instance")
        if not callable(loop_condition):
            raise ValueError("loop_condition must be callable")

        loop_node = LoopNode(node_name, sub_graph, loop_condition, max_iterations, max_execution_time)
        self.nodes[node_name] = loop_node
        
        logger.info(f"Loop node '{node_name}' added with {len(sub_graph.nodes)} sub-graph nodes, max_iterations={max_iterations}")

    def add_conditional_edge(
        self,
        source_node: str,
        condition: Callable[[BaseNode, Any, Optional[Union[str, ToolCall]]], Any],
        condition_mapping: Dict[str, str],
    ) -> None:
        """Add a conditional edge to the execution graph."""
        if not source_node or not source_node.strip():
            raise ValueError("Source node name cannot be empty")
        if source_node not in self.nodes:
            raise ValueError(f"Source node '{source_node}' does not exist in the graph")

        if source_node not in self.edges:
            self.edges[source_node] = []

        self.edges[source_node].append(ConditionalEdge(source_node, condition, condition_mapping))

    def add_edge(self, source_node: str, target_node: str) -> None:
        """Add a direct edge to the execution graph."""
        if not source_node or not source_node.strip():
            raise ValueError("Source node name cannot be empty")
        if not target_node or not target_node.strip():
            raise ValueError("Target node name cannot be empty")
        if source_node not in self.nodes:
            raise ValueError(f"Source node '{source_node}' does not exist in the graph")
        if target_node not in self.nodes:
            raise ValueError(f"Target node '{target_node}' does not exist in the graph")

        if source_node not in self.edges:
            self.edges[source_node] = []

        self.edges[source_node].append(Edge(source_node, target_node))

    def add_human_in_the_loop(self, orchestrator_node_name: str):
        """
        Adds a HumanInTheLoopNode and connects it cyclically to an orchestrator.
        It also dynamically registers the clarification node as a tool for the agent.

        Args:
            orchestrator_node_name (str): The name of the orchestrator node.
            agent (Any): The agent instance whose .tools attribute will be updated.
        """
        if orchestrator_node_name not in self.nodes:
            raise ValueError(f"Orchestrator node '{orchestrator_node_name}' not found.")

        orchestrator = self.nodes[orchestrator_node_name].node_func
        
        if not hasattr(orchestrator, 'tools'):
            raise TypeError("The 'agent' object must have a 'tools' attribute that is a list.")

        # 1. Create and add the HumanInTheLoopNode
        hil_node_name = f"{orchestrator_node_name}_clarification"
    
        if hil_node_name in self.nodes:
            logger.warning(f"HumanInTheLoopNode '{hil_node_name}' already exists.")
        else:
            self.nodes[hil_node_name] = HumanInTheLoopNode(hil_node_name)
            logger.info(f"Added HumanInTheLoopNode: '{hil_node_name}'")

        self.add_edge(orchestrator_node_name, hil_node_name)
        logger.info(f"Connected orchestrator '{orchestrator_node_name}' -> HumanInTheLoopNode '{hil_node_name}' (no automatic return)")
        
        # 3. Define the tool for the agent and register it
        clarification_tool = {
            "type": "function",
            "function": {
                "name": hil_node_name,
                "description": "DO NOT USE THIS TOOL unless the user's task specifically requests asking for user input, clarification, or confirmation. This tool interrupts task execution to ask the user questions. If the task does not explicitly mention getting user input, then DO NOT use this tool - instead, make reasonable assumptions and complete the task with other available tools. Only use this when the task itself says to ask the user something.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "original_input": {
                            "type": "string",
                            "description": "The original user request that explicitly requires human input."
                        },
                        "clarification_prompt": {
                            "type": "string",
                            "description": (
                                "A courteous question or request for confirmation presented to the user. "
                                "If multiple details are required, format the prompt as an enumerated list so it is easy for the user to respond to each item."
                            )
                        }
                    },
                    "required": ["original_input", "clarification_prompt"]
                }
            }
        }

        # Check if the tool is already registered
        if any(tool.get("function", {}).get("name") == hil_node_name for tool in orchestrator.tools):
            logger.warning(f"Tool '{hil_node_name}' is already registered with the agent.")
        else:
            orchestrator.tools.append(clarification_tool)
            logger.info(f"Registered tool '{hil_node_name}' with the agent for '{orchestrator_node_name}'.")

    def compile(self, event_store=None, workflow_id=None) -> CompiledGraph:
        """Compile the execution graph for execution."""
        logger.info("Compiling execution graph...")

        return CompiledGraph(
            nodes=self.nodes.copy(), 
            edges=self.edges.copy(),
            orchestrator_nodes=self.orchestrator_nodes.copy(),
            event_store=event_store,
            workflow_id=workflow_id
        )

    def execute(self, *args, **kwargs) -> str:
        raise NotImplementedError(
            "ExecutionGraph.execute() is not implemented. First compile the graph using .compile()"
        )