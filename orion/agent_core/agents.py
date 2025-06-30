from typing import Callable, Literal, Optional, Union, AsyncIterator, List, Dict, Any
from openai import AsyncOpenAI
from pydantic import BaseModel

from .config import LLMConfig
from .models import ToolCall
from .llm_interface import get_response


def build_agent(
    llm_model: str,
    base_url: str,
    api_key: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    top_p: float = 1.0,
    stream: bool = False,
    schema: Optional[type[BaseModel]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_choice: Literal["auto", "none", "required"] = "auto",
    client: Optional[AsyncOpenAI] = None,
    exponential_backoff_retry: bool = False,
) -> Callable:
    """
    Build a callable async agent with pre-configured settings.

    All agents are async by default - the system handles execution appropriately.

    Args:
        llm_model: The LLM model to use (e.g., 'gpt-4', 'claude-3')
        base_url: The base URL for the API
        api_key: The API key for authentication
        system_prompt: The system prompt to use for all requests
        react_agent: Whether to include ReAct reasoning thoughts
        temperature: Temperature parameter for the LLM (0.0 to 2.0)
        max_tokens: Maximum tokens for responses
        top_p: Top-p parameter for the LLM (0.0 to 1.0)
        schema: Optional schema for structured responses
        tools: Optional tools for function calling
        tool_choice: Whether to include tool calls in the response
        client: Optional pre-configured AsyncOpenAI client

    Returns:
        Callable: An async function that takes prompt and execution_memory and returns a response

    Example:
        >>> agent = build_agent(
        ...     llm_model="gpt-4",
        ...     base_url="https://api.openai.com/v1",
        ...     api_key="your-api-key",
        ...     temperature=0.7
        ... )
        >>> # In async context:
        >>> response = await agent("What is the capital of France?")
        >>> # In sync context:
        >>> response = asyncio.run(agent("What is the capital of France?"))
    """
    config = LLMConfig(
        llm_model=llm_model,
        base_url=base_url,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        stream=stream,
        exponential_backoff_retry=exponential_backoff_retry,
    )

    async def agent(prompt: str) -> Union[str, ToolCall, AsyncIterator[str]]:
        """
        Pre-configured agent that only needs a prompt.

        Args:
            prompt: The user's input prompt
            execution_memory: Optional execution memory

        Returns:
            Union[str, ToolCall]: The LLM response
        """
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        return await get_response(
            config=config,
            prompt=prompt,
            system_prompt=system_prompt,
            schema=schema,
            tools=tools,
            client=client,
            tool_choice=tool_choice,
        )

    # Store system_prompt as an attribute so GraphInspector can access it
    agent.system_prompt = system_prompt
    agent.tools = tools

    return agent
