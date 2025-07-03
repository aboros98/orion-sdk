import inspect
from typing import Callable, Optional, List, Dict, Any
import logging
import os
from dotenv import load_dotenv
from prompts import DESCRIPTION_ENHANCER_SYSTEM_PROMPT
from .models import DescriptionEnhancerResponse

load_dotenv()


logger = logging.getLogger(__name__)


async def enhance_description_with_llm(func_name: str, description: str) -> str:
    from .agents import build_async_agent

    description_enhancer = build_async_agent(llm_model=os.getenv("GENERAL_MODEL"), #type: ignore
                                       base_url=os.getenv("BASE_URL"), #type: ignore
                                       api_key=os.getenv("GEMINI_API_KEY"), #type: ignore
                                       exponential_backoff_retry=True,
                                       system_prompt=DESCRIPTION_ENHANCER_SYSTEM_PROMPT,
                                       schema=DescriptionEnhancerResponse)

    # Pass the function details as user input
    enhanced_description = await description_enhancer(prompt=f"Function name: {func_name}\nFunction description: {description}")

    return enhanced_description.description


async def function_to_schema(func: Callable, enhance_description: bool = False, func_name: Optional[str] = None, needs_memory: bool = False) -> dict:
    """
    Convert a function to a tool schema for use with LLM agents.
    
    Args:
        func: The callable function to process
        enhance_description: Whether to enhance the description using LLM
        func_name: Optional override for the function name
        needs_memory: Whether this function needs access to previous node outputs
    
    Returns:
        Dictionary representing the function schema with optional _needs_memory parameter
    """
    if not callable(func):
        raise ValueError("Input must be a callable function")

    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    # Unwrap decorated functions to get the original function
    original_func = func
    while hasattr(original_func, "__wrapped__"):
        original_func = original_func.__wrapped__

    # If we can't find __wrapped__, try to get the original function from functools.wraps
    if hasattr(original_func, "__closure__") and original_func.__closure__:
        for cell in original_func.__closure__:
            if (
                hasattr(cell.cell_contents, "__name__")
                and cell.cell_contents.__name__ != original_func.__name__
            ):
                # This might be the original function
                potential_original = cell.cell_contents
                if callable(potential_original) and hasattr(potential_original, "__code__"):
                    original_func = potential_original
                    break

    try:
        signature = inspect.signature(original_func)
    except ValueError as e:
        logger.error(f"Failed to get signature for function {original_func.__name__}: {e}")
        raise ValueError(f"Failed to get signature for function {original_func.__name__}: {str(e)}")

    # Initialize parameters dictionary with flexible typing
    parameters: Dict[str, Dict[str, Any]] = {}
    
    if hasattr(original_func, "system_prompt"):
        description = original_func.system_prompt
        parameters["input_prompt"] = {"type": "string", "description": "The input prompt for the described agent."}
        required = ["input_prompt", "_needs_memory"]
        
    else:
        description = original_func.__doc__ or ""

        for param in signature.parameters.values():
            try:
                param_type = type_map.get(param.annotation, "string")
            except KeyError as e:
                logger.error(
                    f"Unknown type annotation {param.annotation} for parameter {param.name}: {e}"
                )
                raise KeyError(
                    f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
                )
            
            param_schema = {"type": param_type}
            
            # Add default value if parameter has one
            if param.default != inspect._empty:
                param_schema["default"] = param.default
            
            parameters[param.name] = param_schema

        required = [
            param.name for param in signature.parameters.values() if param.default == inspect._empty
        ]

    func_name = func_name if func_name else original_func.__name__

    if enhance_description and func_name:
        description = await enhance_description_with_llm(func_name, description) if description != "" else description

    parameters["_needs_memory"] = {"type": "boolean", 
                                   "description": "Whether this function needs access to previous node outputs for context",
                                   "default": False}
        
    return {
        "type": "function",
        "function": {
            "name": func_name,
            "description": description.strip(),
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }


def format_messages(
    prompt: str,
    system_prompt: Optional[str] = None,
) -> List[Dict[str, str]]:
    """
    Format messages for the chat completion API.

    Args:
        prompt: User prompt
        system_prompt: Optional system prompt

    Returns:
        List of message dictionaries
    """
    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": prompt})

    return messages
