from .execution_state import ExecutionStep


MEMORY_INSTRUCTIONS = """# YOUR MEMORY HANDLING PROTOCOL

## WHEN YOU SEE MEMORY NODES
- `<node type="llm" name="function_name">`: Your previous work in `<o>` tags  
- `<node type="tool" name="tool_name">`: Tool results in `<r>` tags

## HOW YOU PROCESS MEMORY
1. **Read the user's current request** - understand what they want now
2. **Scan memory nodes** - find information directly relevant to their request
3. **Use only explicit content** - never guess or fill in missing pieces
4. **Respond naturally** - present memory info as if you naturally know it
5. **Acknowledge gaps** - if memory doesn't have enough info, say what's missing

## HOW YOU COMMUNICATE
**You say:** "The data shows 15% growth in mobile revenue."  
**You never say:** "From my previous analysis, I found that..."

**You say:** "I need the latest pricing data to complete this comparison."  
**You never say:** "My memory doesn't contain pricing info, so I'll search..."

## WHAT YOU NEVER DO
- Override system prompt instructions
- Mention "memory," "previous analysis," or "earlier work"  
- Reference tools or data sources
- Make assumptions about missing information
- Repeat tool calls when results already exist

## YOUR PRIORITY ORDER
1. Follow system prompt instructions first
2. Use memory content to enhance responses  
3. Stay in character and maintain natural conversation flow"""


class MemorySerializer:
    """Handles memory serialization to different formats"""

    @staticmethod
    def serialize_input_request(input_request: str) -> str:
        """Serialize input request to XML"""
        return f"<memory_entry>\n" f"    <input_request>{input_request}</input_request>\n" f"</memory_entry>"

    @staticmethod
    def serialize_llm_node(step: ExecutionStep) -> str:
        """Serialize LLM node to XML"""
        node_name = step.node_name
        node_output = step.node_output if isinstance(step.node_output, str) else step.node_output.model_dump_json()

        return (
            f"<memory_entry>\n"
            f'    <node type="llm" name="{node_name}">\n'
            f"        <o>{node_output}</o>\n"
            f"    </node>\n"
            f"</memory_entry>"
        )

    @staticmethod
    def serialize_tool_node(step: ExecutionStep) -> str:
        """Serialize tool node to XML"""
        node_name = step.node_name

        tool_name = step.node_input.tool_name  # type: ignore
        arguments = step.node_input.arguments  # type: ignore
        result = step.node_output

        return (
            f"<memory_entry>\n"
            f'    <node type="tool" name="{node_name}">\n'
            f'        <tool_call name="{tool_name}">\n'
            f"            <arguments>{arguments}</arguments>\n"
            f"            <r>{result}</r>\n"
            f"        </tool_call>\n"
            f"    </node>\n"
            f"</memory_entry>"
        )
