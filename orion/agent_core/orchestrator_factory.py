from typing import List, Dict, Any

from .agents import build_async_agent
from prompts import ORCHESTRATOR_SYSTEM_PROMPT_TEMPLATE


def _build_system_prompt(tools: List[Dict[str, Any]]) -> str:
    """Generate a concise system prompt for the orchestrator agent.

    The prompt describes the agent's routing role and enumerates the available
    tools with their names and descriptions.  This allows the LLM to make an
    informed decision about which tool to call.
    """
    if not tools:
        raise ValueError("Tools list cannot be empty when building an orchestrator agent")

    # Format tool descriptions for the prompt
    tool_descriptions = []
    for tool in tools:
        if "function" in tool:
            func_info = tool["function"]
            name = func_info.get("name", "unknown")
            description = func_info.get("description", "No description available")
            tool_descriptions.append(f"• {name}: {description}")

    tools_descriptions_text = "\n".join(tool_descriptions)

    # Format the template with tool descriptions
    return ORCHESTRATOR_SYSTEM_PROMPT_TEMPLATE.format(tools_descriptions=tools_descriptions_text)


def create_orchestrator(
    *,
    tools: List[Dict[str, Any]],
    llm_model: str,
    base_url: str,
    api_key: str,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    top_p: float = 1.0,
    **kwargs,
):
    """Factory that returns an **async** orchestrator agent ready to be used inside an OrchestratorNode.

    Parameters
    ----------
    tools: List of tool JSON schemas (as accepted by the OpenAI function-calling API).
    llm_model / base_url / api_key: LLM connection details forwarded to ``build_agent``.
    temperature, max_tokens, top_p: Usual sampling parameters (default to deterministic behaviour).
    tool_choice: Passed through to ``build_agent`` (defaults to "auto").

    Returns
    -------
    Callable[[str], Awaitable[ToolCall]]
        The async agent produced by ``build_agent``.
    """

    system_prompt = _build_system_prompt(tools)

    return build_async_agent(
        llm_model=llm_model,
        base_url=base_url,
        api_key=api_key,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        tools=tools,
        tool_choice="auto",
        exponential_backoff_retry=True
    )
