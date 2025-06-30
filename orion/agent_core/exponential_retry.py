import asyncio
import logging
from typing import Callable, Any
import openai
from .config import ExponentialBackoffRetryConfig

logger = logging.getLogger(__name__)


def should_retry_error(error: Exception) -> bool:
    """
    Check if an error should trigger a retry.

    Retries on most API errors except:
    - Connection errors (network issues)
    - Authentication errors (bad API key)
    """
    # Don't retry on authentication errors (bad API key)
    if isinstance(error, openai.AuthenticationError):
        return False

    # Don't retry on connection errors (network issues)
    if isinstance(error, (openai.APIConnectionError, ConnectionError)):
        return False

    # Retry on all other OpenAI API errors
    if isinstance(error, openai.APIError):
        return True

    # Retry on timeout errors
    if isinstance(error, asyncio.TimeoutError):
        return True

    # Check HTTP status codes for other errors
    if hasattr(error, "status_code"):
        status_code = getattr(error, "status_code")
        # Don't retry on client errors (except rate limits)
        if 400 <= status_code < 500:
            return status_code == 429  # Only retry on rate limits
        elif 500 <= status_code < 600:
            return True

    return False


def calculate_exponential_delay(attempt: int, config: ExponentialBackoffRetryConfig) -> float:
    """Calculate exponential backoff delay."""
    delay = config.base_delay * (2 ** (attempt - 1))
    return min(delay, config.max_delay)


async def with_retry(
    func: Callable[..., Any], config: ExponentialBackoffRetryConfig, *args, **kwargs
) -> Any:
    """
    Execute a function with retry logic.

    Args:
        func: The async function to execute
        config: SimpleRetryConfig with retry parameters
        *args, **kwargs: Arguments to pass to the function

    Returns:
        The result of the function call

    Raises:
        The last exception if all retries are exhausted
    """
    for attempt in range(config.max_retries + 1):  # +1 for initial attempt
        try:
            if attempt > 0:
                logger.debug(f"Retrying {func.__name__}, attempt {attempt + 1}")

            result = await func(*args, **kwargs)

            if attempt > 0:
                logger.info(f"{func.__name__} succeeded on attempt {attempt + 1}")

            return result

        except Exception as e:
            if not should_retry_error(e):
                logger.debug(f"Error {type(e).__name__} is not retryable for {func.__name__}")
                raise e

            # Check if we have retries left
            if attempt >= config.max_retries:
                logger.error(f"All {config.max_retries} retries exhausted for {func.__name__}")
                raise e

            # Calculate delay and wait
            delay = calculate_exponential_delay(attempt + 1, config)
            logger.warning(
                f"{func.__name__} failed on attempt {attempt + 1} with {type(e).__name__}: {str(e)}. "
                f"Retrying in {delay:.2f} seconds..."
            )

            await asyncio.sleep(delay)
