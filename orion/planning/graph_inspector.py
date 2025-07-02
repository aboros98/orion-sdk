"""Graph capability inspector for understanding available graph capabilities."""

from typing import TYPE_CHECKING
import inspect

if TYPE_CHECKING:
    from orion.graph_core.compiled_graph import CompiledGraph


class GraphInspector:
    """Inspector for analyzing graph capabilities and generating examples."""
    
    def __init__(self, compiled_graph: "CompiledGraph"):
        """Store compiled graph reference"""
        self.compiled_graph = compiled_graph

    def get_available_capabilities(self) -> str:
        """
        Return a concise, factual overview of what each node in the compiled graph can do.
        The result is grouped by node category so downstream prompts can present
        capabilities in a predictable structure.
        """
        llm_capabilities: list[str] = []
        tool_capabilities: list[str] = []
        special_capabilities: list[str] = []

        for node_name, node in self.compiled_graph.nodes.items():
            # Ignore sentinel nodes used by the engine
            if node_name in {"__start__", "__end__"}:
                continue

            node_cls = node.__class__.__name__

            # ---- SPECIAL NODES -------------------------------------------------
            if hasattr(node, 'is_memory_reader'):
                special_capabilities.append(
                    f"  - {node_name} (Memory-enabled LLM): Provides the LLM with\n    execution-memory context so it can use previous node outputs."
                )
                continue
            if node_cls == "OrchestratorNode":
                special_capabilities.append(
                    f"  - {node_name} (OrchestratorNode): Routes each user request or intermediate\n    result to the next appropriate node based on simple rules and memory."
                )
                continue
            if node_cls == "HumanInTheLoopNode":
                special_capabilities.append(
                    f"  - {node_name} (HumanInTheLoopNode): Interrupts the workflow to collect\n    clarification from a human when the input is ambiguous."
                )
                continue
            if node_cls == "LoopNode":
                max_iter = getattr(node, "max_iterations", "n/a")
                special_capabilities.append(
                    f"  - {node_name} (LoopNode): Repeats a sub-workflow until a condition is false\n    (max {max_iter} iterations)."
                )
                continue

            # ---- TOOL NODES ----------------------------------------------------
            if hasattr(node.node_func, "_is_tool"):
                # Description: take first non-empty line of docstring or fallback to function name.
                doc = (node.node_func.__doc__ or "").strip()
                if doc:
                    capability_line = doc.split("\n", 1)[0].rstrip(".")
                else:
                    capability_line = node.node_func.__name__.replace("_", " ").title()
                tool_capabilities.append(f"  - {node_name}: {capability_line}")
                continue

            # ---- LLM NODES -----------------------------------------------------
            capability_line = self._extract_llm_capability(node.node_func)
            llm_capabilities.append(f"  - {node_name}: {capability_line}")

        parts: list[str] = ["Available graph capabilities:"]

        if llm_capabilities:
            parts.append("\nLLM NODES:")
            parts.extend(llm_capabilities)

        if tool_capabilities:
            parts.append("\nTOOL NODES:")
            parts.extend(tool_capabilities)

        if special_capabilities:
            parts.append("\nSPECIAL NODES:")
            parts.extend(special_capabilities)

        # Final note so downstream prompts know orchestration is automatic.
        parts.append(
            "\nThe orchestrator node (if present) decides routing; callers do not\nneed to reference specific node names."  # noqa: E501
        )

        return "\n".join(parts)

    def _extract_llm_capability(self, node_func) -> str:
        """Extract capability description for LLM nodes from system prompt."""
        try:
            # First, check if the function has system_prompt attribute (from build_agent)
            if hasattr(node_func, 'system_prompt') and node_func.system_prompt:
                system_prompt = node_func.system_prompt.strip()
                # Extract first meaningful line from system prompt
                lines = [line.strip() for line in system_prompt.split('\n') if line.strip()]
                if lines:
                    first_line = lines[0]
                    # Remove common prefixes and make it a capability description
                    first_line = first_line.replace('You are a ', '').replace('You are an ', '')
                    first_line = first_line.replace('You are ', '').rstrip('.')
                    return first_line.capitalize()
            
            # Fallback: Try to access system prompt from closure (old method)
            if hasattr(node_func, '__closure__') and node_func.__closure__:
                for cell in node_func.__closure__:
                    if hasattr(cell.cell_contents, 'system_prompt'):
                        system_prompt = cell.cell_contents.system_prompt
                        if system_prompt:
                            lines = [line.strip() for line in system_prompt.strip().split('\n') if line.strip()]
                            if lines:
                                first_line = lines[0]
                                first_line = first_line.replace('You are a ', '').replace('You are an ', '')
                                first_line = first_line.replace('You are ', '').rstrip('.')
                                return first_line.capitalize()
            
            # Try to get from function signature or defaults
            sig = inspect.signature(node_func)
            for param in sig.parameters.values():
                if param.default != param.empty and isinstance(param.default, str):
                    if 'system' in param.name.lower() or 'prompt' in param.name.lower():
                        lines = [line.strip() for line in param.default.strip().split('\n') if line.strip()]
                        if lines:
                            first_line = lines[0]
                            first_line = first_line.replace('You are a ', '').replace('You are an ', '')
                            first_line = first_line.replace('You are ', '').rstrip('.')
                            return first_line.capitalize()
            
            # Check function docstring
            if node_func.__doc__:
                return node_func.__doc__.strip().split('\n')[0]
                
        except Exception as e:
            # Log the error for debugging but don't crash
            print(f"Warning: Could not extract LLM capability for node function: {e}")
        
        # Fallback to generic description
        return "General reasoning and analysis"
