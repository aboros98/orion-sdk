from .workflow import WorkflowGraph
from .edges import Edge, ConditionalEdge
from .nodes import LLMNode, ToolNode, MemoryReaderNode, OrchestratorNode, LoopNode
from orion.memory_core import ExecutionMemory
import os
import webbrowser


def to_mermaid(graph: WorkflowGraph) -> str:
    """
    Generate a clean Mermaid flowchart definition for the given execution graph.
    Supports all node types with plain professional styling and explicit memory arrows.
    
    Features:
    - Clean professional design without emojis
    - Plain color scheme with light backgrounds
    - Explicit memory read/write arrows
    - Distinctive shapes for different node types
    - Automatic memory node detection and inclusion
    
    Returns:
        str: Mermaid flowchart definition with clean styling
    """
    lines = ["flowchart TD"]

    # Track if we have memory-related functionality
    has_memory_functionality = _has_memory_functionality(graph)
    
    # Define node shapes based on node type with clean styling (excluding memory nodes)
    for node_name, node in graph.nodes.items():
        # Skip memory nodes as they will be in isolated subgraph
        if isinstance(node, ExecutionMemory) or ('memory' in node_name.lower() and not isinstance(node, MemoryReaderNode)):
            continue
            
        if node_name == "__start__":
            lines.append(f"    {node_name}([\"{node_name}\"]):::startNode")
        elif node_name == "__end__":
            lines.append(f"    {node_name}([\"{node_name}\"]):::endNode")
        elif isinstance(node, MemoryReaderNode):
            # Special hexagon shape for memory reader nodes
            lines.append("    " + node_name + "{\"" + node_name + "\"}:::memoryReaderNode")
        elif isinstance(node, OrchestratorNode):
            # Diamond shape for orchestrator/decision nodes
            lines.append("    " + node_name + "{\"" + node_name + "\"}:::orchestratorNode")
        elif isinstance(node, LoopNode):
            # Special container shape for loop nodes
            lines.append("    " + node_name + "[[\"" + node_name + "\"]]:::loopNode")
        elif isinstance(node, LLMNode):
            # Rounded rectangle for LLM nodes
            lines.append("    " + node_name + "(\"" + node_name + "\"):::llmNode")
        elif isinstance(node, ToolNode):
            # Rectangle for tool nodes
            lines.append(f"    {node_name}[\"{node_name}\"]:::toolNode")
        else:
            # Default shape for unknown node types
            lines.append(f"    {node_name}[\"{node_name}\"]:::defaultNode")

    # Add memory node in isolated subgraph if memory functionality is detected
    if has_memory_functionality and not _has_explicit_memory_node(graph):
        lines.append("")
        lines.append("    %% === Memory Layer (Isolated) ===")
        lines.append("    subgraph MemoryLayer [\"Memory Layer\"]")
        lines.append("        ExecutionMemory[(\"ExecutionMemory\")]:::implicitMemoryNode")
        lines.append("    end")

    # Handle explicit memory nodes in isolated subgraph
    explicit_memory_nodes = []
    for node_name, node in graph.nodes.items():
        if isinstance(node, ExecutionMemory) or ('memory' in node_name.lower() and not isinstance(node, MemoryReaderNode)):
            explicit_memory_nodes.append((node_name, node))
    
    if explicit_memory_nodes:
        lines.append("")
        lines.append("    %% === Memory Layer (Isolated) ===")
        lines.append("    subgraph MemoryLayer [\"Memory Layer\"]")
        for memory_node_name, memory_node in explicit_memory_nodes:
            if isinstance(memory_node, ExecutionMemory):
                lines.append(f"        {memory_node_name}[(\"{memory_node_name}\")]:::memoryNode")
            else:
                lines.append(f"        {memory_node_name}[(\"{memory_node_name}\")]:::memoryNode")
        lines.append("    end")

    # Add clean CSS classes with plain colors
    lines.append("")
    lines.append("    %% === Node Styling ===")
    lines.append("    classDef startNode fill:#e8f5e8,stroke:#4caf50,stroke-width:2px,color:#333")
    lines.append("    classDef endNode fill:#ffebee,stroke:#f44336,stroke-width:2px,color:#333")
    lines.append("    classDef llmNode fill:#e3f2fd,stroke:#2196f3,stroke-width:2px,color:#333")
    lines.append("    classDef toolNode fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#333")
    lines.append("    classDef orchestratorNode fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px,color:#333")
    lines.append("    classDef loopNode fill:#eceff1,stroke:#607d8b,stroke-width:2px,color:#333,stroke-dasharray:5 5")
    lines.append("    classDef memoryNode fill:#fce4ec,stroke:#e91e63,stroke-width:2px,color:#333,stroke-dasharray:3 3")
    lines.append("    classDef memoryReaderNode fill:#e0f2f1,stroke:#009688,stroke-width:2px,color:#333")
    lines.append("    classDef implicitMemoryNode fill:#fce4ec,stroke:#e91e63,stroke-width:2px,color:#333,stroke-dasharray:3 3")
    lines.append("    classDef defaultNode fill:#f5f5f5,stroke:#757575,stroke-width:2px,color:#333")
    lines.append("")
    lines.append("    %% === Subgraph Styling ===")
    lines.append("    style MemoryLayer fill:#f8f9fa,stroke:#6c757d,stroke-width:1px,stroke-dasharray:2 2")
    lines.append("")

    # Define edges with clean styling
    lines.append("    %% === Graph Connections ===")
    for source_node, edge_list in graph.edges.items():
        for edge in edge_list:
            if isinstance(edge, ConditionalEdge):
                # Dashed lines for conditional edges with labels
                for label, target in edge.condition_mapping.items():
                    clean_label = _clean_label(label)
                    lines.append(f"    {edge.source} -.->|{clean_label}| {target}")
            elif isinstance(edge, Edge):
                # Solid lines for regular edges
                lines.append(f"    {edge.source} --> {edge.target}")

    # Add memory read/write arrows
    lines.append("")
    lines.append("    %% === Memory Interactions ===")
    
    memory_node_name = "ExecutionMemory"
    # Find explicit memory node if it exists
    for node_name, node in graph.nodes.items():
        if isinstance(node, ExecutionMemory):
            memory_node_name = node_name
            break
    
    # Add memory node if it doesn't exist but is needed
    if has_memory_functionality and not _has_explicit_memory_node(graph):
        # Nodes that read from memory
        for node_name, node in graph.nodes.items():
            if isinstance(node, (MemoryReaderNode, OrchestratorNode, LoopNode)):
                lines.append(f"    {memory_node_name} -->|read| {node_name}")
        
        # Nodes that write to memory (processing nodes except orchestrators)
        for node_name, node in graph.nodes.items():
            if isinstance(node, (LLMNode, ToolNode, MemoryReaderNode, LoopNode)):
                if node_name not in ["__start__", "__end__"]:
                    lines.append(f"    {node_name} -->|write| {memory_node_name}")
    elif _has_explicit_memory_node(graph):
        # Handle explicit memory nodes
        for node_name, node in graph.nodes.items():
            if isinstance(node, (MemoryReaderNode, OrchestratorNode, LoopNode)):
                lines.append(f"    {memory_node_name} -->|read| {node_name}")
        
        for node_name, node in graph.nodes.items():
            if isinstance(node, (LLMNode, ToolNode, MemoryReaderNode, LoopNode)):
                if node_name not in ["__start__", "__end__"] and node_name != memory_node_name:
                    lines.append(f"    {node_name} -->|write| {memory_node_name}")

    return "\n".join(lines)


def _has_memory_functionality(graph: WorkflowGraph) -> bool:
    """Check if the graph has any memory-related functionality."""
    for node_name, node in graph.nodes.items():
        if isinstance(node, (MemoryReaderNode, OrchestratorNode, LoopNode)):
            return True
        if 'memory' in node_name.lower():
            return True
    return False


def _has_explicit_memory_node(graph: WorkflowGraph) -> bool:
    """Check if the graph has an explicit memory node."""
    for node_name, node in graph.nodes.items():
        if isinstance(node, ExecutionMemory):
            return True
        if 'memory' in node_name.lower() and not isinstance(node, MemoryReaderNode):
            return True
    return False


def _clean_label(label: str) -> str:
    """Clean and format edge labels for Mermaid display."""
    if not label:
        return ""
    # Truncate long labels and escape special characters
    if len(label) > 15:
        label = label[:12] + "..."
    # Replace characters that might break Mermaid syntax
    label = label.replace('"', "'").replace('\n', ' ').replace('|', '/')
    return label


def render_to_html(graph: WorkflowGraph, output_path: str = "graph.html") -> str:
    """
    Generates an HTML file with the original simple styling.

    Args:
        graph: The WorkflowGraph to render.
        output_path: The path to save the HTML file to.

    Returns:
        The absolute path to the generated HTML file.
    """
    mermaid_code = to_mermaid(graph)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Interactive Execution Graph</title>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom/dist/svg-pan-zoom.min.js"></script>
        <style>
            html, body {{
                height: 100%;
                margin: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: #f0f2f5;
                overflow: hidden;
            }}
            #graph-container {{
                width: 100%;
                height: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .mermaid svg {{
                cursor: move;
            }}
            h1 {{
                position: fixed;
                top: 20px;
                left: 20px;
                color: #343a40;
                background-color: rgba(255, 255, 255, 0.9);
                padding: 10px 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin: 0;
                z-index: 1000;
            }}
        </style>
    </head>
    <body>
        <h1>Workflow Graph</h1>
        <div id="graph-container">
            <div class="mermaid">
                {mermaid_code}
            </div>
        </div>

        <script>
            // Wait for the entire page to load before initializing the graph
            window.onload = function () {{
                mermaid.initialize({{ startOnLoad: false }});
                const mermaidContainer = document.querySelector('.mermaid');
                
                mermaid.render('the-svg', mermaidContainer.textContent, (svgCode) => {{
                    mermaidContainer.innerHTML = svgCode;
                    const svgElement = mermaidContainer.querySelector('svg');

                    if (svgElement) {{
                        svgPanZoom(svgElement, {{
                            zoomEnabled: true,
                            controlIconsEnabled: true,
                            fit: true,
                            center: true
                        }});
                    }}
                }});
            }};
        </script>
    </body>
    </html>
    """

    with open(output_path, "w") as f:
        f.write(html_content)

    abs_path = os.path.abspath(output_path)
    webbrowser.open(f"file://{abs_path}")

    return abs_path
