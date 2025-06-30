from pydantic import BaseModel
from typing import Any, Dict


class ToolCall(BaseModel):
    """
    Response from a tool call.

    Attributes:
        tool_name: The name of the tool that was called
        arguments: The arguments passed to the tool
    """

    tool_name: str
    arguments: Dict[str, Any]


class Response(BaseModel):
    """
    Response from the LLM.

    Attributes:
        thought: Optional reasoning thought process
        response: The text response from the LLM
    """

    response: str
