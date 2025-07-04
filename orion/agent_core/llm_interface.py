from typing import Any, Optional, Literal, Union, AsyncIterator, List, Dict, Iterator
from openai import AsyncOpenAI, OpenAI, AsyncStream, Stream
from pydantic import BaseModel
import logging
import json

from .config import LLMConfig
from .models import ToolCall
from .client import get_or_create_client, get_or_create_sync_client
from .utils import format_messages
from .exponential_retry import with_retry, with_sync_retry

logger = logging.getLogger(__name__)


def _parse_tool_call(response) -> ToolCall:
    """Parse tool call from response."""
    tool_call = response.choices[0].message.tool_calls[0]

    return ToolCall(
        tool_name=tool_call.function.name,
        arguments=json.loads(tool_call.function.arguments),
    )


def _get_response_content(response) -> str:
    """Get response content from completion."""
    return response.choices[0].message.content


def _has_tool_calls(response) -> bool:
    """Check if response has tool calls."""
    return (
        hasattr(response, "choices")
        and len(response.choices) > 0
        and hasattr(response.choices[0].message, "tool_calls")
        and response.choices[0].message.tool_calls
    )


def _is_stream_response(response) -> bool:
    """Check if response is a stream."""
    return isinstance(response, (AsyncStream, Stream))


def _get_parsed_response(response):
    """Get parsed response from schema response."""
    return response.choices[0].message.parsed


async def _create_async_stream_generator(response: AsyncStream):
    """Create async generator for streaming response."""
    async for chunk in response:
        if chunk.choices and len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content


def _create_sync_stream_generator(response: Stream):
    """Create sync generator for streaming response."""
    for chunk in response:
        if chunk.choices and len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content


def _get_chat_completion_func(client, schema):
    """Get the appropriate chat completion function."""
    if schema:
        return client.beta.chat.completions.parse
    else:
        return client.chat.completions.create


def _prepare_kwargs_for_retry(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare kwargs for retry by removing non-serializable items."""
    if not kwargs.get("response_format"):
        kwargs.pop("response_format")
    else:
        kwargs.pop("stream")
        kwargs.pop("tools")
        kwargs.pop("tool_choice")

    return kwargs


# ASYNC FUNCTIONS


async def _call_with_retry_if_configured(func, config: LLMConfig, *args, **kwargs):
    """Call function with retry if config has retry enabled."""
    kwargs = _prepare_kwargs_for_retry(kwargs)

    if config.retry_config:
        return await with_retry(func, config.retry_config, *args, **kwargs)
    else:
        return await func(*args, **kwargs)


async def get_response(
    config: LLMConfig,
    prompt: str,
    system_prompt: Optional[str] = None,
    client: Optional[AsyncOpenAI] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_choice: Literal["auto", "none", "required"] = "auto",
    schema: Optional[type[BaseModel]] = None,
) -> Union[str, ToolCall, AsyncIterator[str]]:
    """
    Get a response from the LLM.

    Args:
        config: LLM configuration parameters
        prompt: User's input prompt
        system_prompt: Optional system prompt to set context
        client: Optional pre-configured AsyncOpenAI client
        tools: Optional list of tools to use
        tool_choice: Optional tool choice mode
        schema: Optional schema to use for parsing the response

    Returns:
        Union[str, ToolCall, AsyncIterator[str]]: The LLM's response

    Raises:
        Exception: If the API call fails
    """
    if client is None:
        client = await get_or_create_client(config)

    messages = format_messages(system_prompt=system_prompt, prompt=prompt)

    try:
        chat_completion_func = _get_chat_completion_func(client, schema)

        response = await _call_with_retry_if_configured(
            lambda **kwargs: chat_completion_func(**kwargs),
            config,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            response_format=schema,
            **config.to_dict(),
        )

        if schema:
            return _get_parsed_response(response)

        if _is_stream_response(response):
            return _create_async_stream_generator(response)
        elif _has_tool_calls(response):
            return _parse_tool_call(response)
        else:
            return _get_response_content(response)

    except Exception as e:
        logger.error(f"Failed to get LLM response: {e}")
        raise Exception(f"LLM API call failed: {e}")


# SYNC FUNCTIONS


def _call_sync_with_retry_if_configured(func, config: LLMConfig, *args, **kwargs):
    """Call function with retry if config has retry enabled (synchronous version)."""
    kwargs = _prepare_kwargs_for_retry(kwargs)

    if config.retry_config:
        return with_sync_retry(func, config.retry_config, *args, **kwargs)
    else:
        return func(*args, **kwargs)


def get_sync_response(
    config: LLMConfig,
    prompt: str,
    system_prompt: Optional[str] = None,
    client: Optional[OpenAI] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_choice: Literal["auto", "none", "required"] = "auto",
    schema: Optional[type[BaseModel]] = None,
) -> Union[str, ToolCall, Iterator[str]]:
    """
    Get a response from the LLM (synchronous version).

    Args:
        config: LLM configuration parameters
        prompt: User's input prompt
        system_prompt: Optional system prompt to set context
        client: Optional pre-configured OpenAI client
        tools: Optional list of tools to use
        tool_choice: Optional tool choice mode
        schema: Optional schema to use for parsing the response

    Returns:
        Union[str, ToolCall, Iterator[str]]: The LLM's response

    Raises:
        Exception: If the API call fails
    """
    if client is None:
        client = get_or_create_sync_client(config)

    messages = format_messages(system_prompt=system_prompt, prompt=prompt)

    try:
        chat_completion_func = _get_chat_completion_func(client, schema)

        response = _call_sync_with_retry_if_configured(
            lambda **kwargs: chat_completion_func(**kwargs),
            config,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            response_format=schema,
            **config.to_dict(),
        )

        if schema:
            return _get_parsed_response(response)

        if _is_stream_response(response):
            return _create_sync_stream_generator(response)
        elif _has_tool_calls(response):
            return _parse_tool_call(response)
        else:
            return _get_response_content(response)

    except Exception as e:
        logger.error(f"Failed to get LLM response: {e}")
        raise Exception(f"LLM API call failed: {e}")
