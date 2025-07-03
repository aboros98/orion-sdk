from typing import Any, Optional, Literal, Union, AsyncIterator, List, Dict
from openai import AsyncOpenAI, AsyncStream
from pydantic import BaseModel
import logging
import json
import os
from datetime import datetime

from .config import LLMConfig
from .models import ToolCall
from .client import get_or_create_client
from .utils import format_messages
from .exponential_retry import with_retry

logger = logging.getLogger(__name__)


def log_messages_to_file(messages: List[Dict[str, str]], log_dir: str = "debug_logs"):
    """Log messages to a single debug file with timestamp."""
    os.makedirs(log_dir, exist_ok=True)
    
    filename = f"{log_dir}/llm_messages.jsonl"  # JSON Lines format

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "messages": messages
    }
    
    # Append to single file
    with open(filename, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    logger.debug(f"Messages logged to {filename}")


async def _call_with_retry_if_configured(func, config: LLMConfig, *args, **kwargs):
    """Call function with retry if config has retry enabled."""
    if not kwargs.get("response_format"):
        kwargs.pop("response_format")
    else:
        kwargs.pop("stream")
        kwargs.pop("tools")
        kwargs.pop("tool_choice")

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
        chat_completion_func = (
            client.chat.completions.create if schema is None else client.beta.chat.completions.parse
        )
        
        response = await _call_with_retry_if_configured(
            lambda **kwargs: chat_completion_func(**kwargs),
            config,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            response_format=schema,
            **config.to_dict(),
        )

        log_messages_to_file(messages)

        if schema:
            return response.choices[0].message.parsed

        if isinstance(response, AsyncStream):
            async def stream_generator():
                async for chunk in response:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

            return stream_generator()
        elif response.choices[0].message.tool_calls:
            tool_call_data = response.choices[0].message.tool_calls[0]

            return ToolCall(
                tool_name=tool_call_data.function.name,
                arguments=json.loads(tool_call_data.function.arguments),
            )
        else:
            return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Failed to get LLM response: {e}")
        raise Exception(f"LLM API call failed: {e}")
