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
