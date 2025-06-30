from dataclasses import dataclass
from typing import Optional


class ExponentialBackoffRetryConfig:
    """Simple configuration for retry behavior."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        """
        Initialize simple retry configuration.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for exponential backoff
            max_delay: Maximum delay between retries
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay


@dataclass
class LLMConfig:
    """
    Configuration for LLM parameters and API settings.

    Attributes:
        llm_model: The name of the LLM model to use (e.g., 'gpt-4', 'claude-3')
        base_url: The base URL for the API endpoint
        api_key: The API key for authentication
        temperature: Controls randomness in responses (0.0 = deterministic, 1.0 = very random)
        max_tokens: Maximum number of tokens in the response
        top_p: Controls diversity via nucleus sampling (0.0 to 1.0)
        stream: Whether to enable streaming responses (default: False)
        retry_config: Optional SimpleRetryConfig for retry behavior (None = no retries)
    """

    llm_model: str
    api_key: str
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    stream: bool = False
    exponential_backoff_retry: bool = False

    def __post_init__(self):
        """Validate configuration parameters after initialization."""
        self.retry_config = (
            ExponentialBackoffRetryConfig() if self.exponential_backoff_retry else None
        )

        if not self.llm_model:
            raise ValueError("llm_model cannot be empty")
        if not self.api_key:
            raise ValueError("api_key cannot be empty")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if not 0.0 <= self.top_p <= 1.0:
            raise ValueError("top_p must be between 0.0 and 1.0")

    def to_dict(self) -> dict:
        """Convert configuration to dictionary for API calls."""
        return {
            "model": self.llm_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stream": self.stream,
        }
