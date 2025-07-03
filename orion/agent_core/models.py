from pydantic import BaseModel, Field
from typing import Any, Dict


class ToolCall(BaseModel):
    """
    Response from a tool call.

    Attributes:
        tool_name: The name of the tool that was called
        arguments: The arguments passed to the tool
    """

    tool_name: str = Field(description="The name of the tool that was called")
    arguments: Dict[str, Any] = Field(description="The arguments passed to the tool")


class DescriptionEnhancerResponse(BaseModel):
    """
    Response from the description enhancer.

    Attributes:
        description: The enhanced description
    """

    description: str = Field(description="The enhanced description of the function.")