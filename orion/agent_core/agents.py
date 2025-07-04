from typing import Callable, Literal, Optional, Union, List, Dict, Any, AsyncIterator, Iterator
from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel

from .config import LLMConfig
from .models import ToolCall
from .llm_interface import get_response, get_sync_response


def build_async_agent(
    llm_model: str,
    base_url: str,
    api_key: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 8192,
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

    Args:
        llm_model: The LLM model to use (e.g., 'gpt-4', 'claude-3')
        base_url: The base URL for the API
        api_key: The API key for authentication
        system_prompt: The system prompt to use for all requests
        temperature: Temperature parameter for the LLM (0.0 to 2.0)
        max_tokens: Maximum tokens for responses
        top_p: Top-p parameter for the LLM (0.0 to 1.0)
        stream: Whether to enable streaming responses
        schema: Optional schema for structured responses
        tools: Optional tools for function calling
        tool_choice: Whether to include tool calls in the response
        client: Optional pre-configured AsyncOpenAI client
        exponential_backoff_retry: Whether to enable exponential backoff retry

    Returns:
        Callable: An async function that takes prompt and returns a response
    """
    # Create config
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
        """Pre-configured async agent that only needs a prompt."""
        if not prompt or not prompt.strip():
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

    # Set attributes for GraphInspector access
    agent.system_prompt = system_prompt
    agent.tools = tools

    return agent


def build_sync_agent(
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
    client: Optional[OpenAI] = None,
    exponential_backoff_retry: bool = False,
) -> Callable:
    """
    Build a callable sync agent with pre-configured settings.

    Args:
        llm_model: The LLM model to use (e.g., 'gpt-4', 'claude-3')
        base_url: The base URL for the API
        api_key: The API key for authentication
        system_prompt: The system prompt to use for all requests
        temperature: Temperature parameter for the LLM (0.0 to 2.0)
        max_tokens: Maximum tokens for responses
        top_p: Top-p parameter for the LLM (0.0 to 1.0)
        stream: Whether to enable streaming responses
        schema: Optional schema for structured responses
        tools: Optional tools for function calling
        tool_choice: Whether to include tool calls in the response
        client: Optional pre-configured OpenAI client
        exponential_backoff_retry: Whether to enable exponential backoff retry

    Returns:
        Callable: A sync function that takes prompt and returns a response
    """
    # Create config
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

    def agent(prompt: str) -> Union[str, ToolCall, Iterator[str]]:
        """Pre-configured sync agent that only needs a prompt."""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        return get_sync_response(
            config=config,
            prompt=prompt,
            system_prompt=system_prompt,
            schema=schema,
            tools=tools,
            client=client,
            tool_choice=tool_choice,
        )

    # Set attributes for GraphInspector access
    agent.system_prompt = system_prompt
    agent.tools = tools

    return agent
