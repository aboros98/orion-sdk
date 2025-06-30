from typing import Callable


def tool(func: Callable) -> Callable:
    """
    Decorator to mark a function as a tool that can be called by LLM agents.

    This decorator simply adds the '_is_tool' attribute to the function,
    which is used by the ExecutionGraph to identify tool functions.

    Usage:
        @tool
        def my_func(): pass

    Args:
        func: The function to mark as a tool

    Returns:
        Callable: Original function with _is_tool attribute added

    Example:
        >>> @tool
        ... def add_numbers(a: int, b: int) -> int:
        ...     \"\"\"Add two numbers together.\"\"\"
        ...     return a + b
    """
    setattr(func, "_is_tool", True)

    return func
