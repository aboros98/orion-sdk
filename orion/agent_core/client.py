from openai import AsyncOpenAI
from .config import LLMConfig
from typing import Dict, Optional
import asyncio
import hashlib
import logging
import weakref
import httpx
from contextlib import AsyncExitStack

logger = logging.getLogger(__name__)


class ClientPool:
    """
    Manages a pool of AsyncOpenAI clients with connection pooling and reuse.
    
    Features:
    - Client reuse based on configuration
    - HTTP connection pooling 
    - Automatic cleanup of unused clients
    - Thread-safe access
    """
    
    def __init__(self):
        self._clients: Dict[str, AsyncOpenAI] = {}
        self._client_refs: Dict[str, weakref.ref] = {}
        self._lock = asyncio.Lock()
        self._exit_stack = AsyncExitStack()
    
    def _get_client_key(self, config: LLMConfig) -> str:
        """Generate a unique key for client identification."""
        # Create a hash based on base_url and first 10 chars of API key
        # This ensures same config reuses the same client
        key_data = f"{config.base_url}:{config.api_key[:10]}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]
    
    async def get_client(self, config: LLMConfig) -> AsyncOpenAI:
        """
        Get or create a client for the given configuration.
        
        Args:
            config: LLM configuration
            
        Returns:
            AsyncOpenAI: Reused or newly created client
        """
        client_key = self._get_client_key(config)
        
        async with self._lock:
            # Check if we have a valid client
            if client_key in self._clients:
                client = self._clients[client_key]
                if client is not None:
                    logger.debug(f"Reusing existing client for key: {client_key}")
                    return client
            
            # Create new client with optimized settings
            logger.info(f"Creating new optimized client for key: {client_key}")
            client = await self._create_optimized_client(config)
            
            # Store client and set up cleanup
            self._clients[client_key] = client
            self._client_refs[client_key] = weakref.ref(
                client, 
                lambda ref: self._cleanup_client(client_key)
            )
            
            return client
    
    async def _create_optimized_client(self, config: LLMConfig) -> AsyncOpenAI:
        """Create a new AsyncOpenAI client with optimized HTTP settings."""
        
        # Create optimized HTTP client with connection pooling
        http_client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_keepalive_connections=20,  # Keep 20 connections alive
                max_connections=100,           # Max 100 total connections
                keepalive_expiry=30.0         # Keep connections alive for 30s
            ),
            timeout=httpx.Timeout(
                connect=10.0,  # 10s to connect
                read=60.0,     # 60s to read response
                write=10.0,    # 10s to write request
                pool=5.0       # 5s to get connection from pool
            ),
            follow_redirects=True,
            http2=True  # Enable HTTP/2 if available
        )
        
        # Register for cleanup
        await self._exit_stack.enter_async_context(http_client)
        
        try:
            client = AsyncOpenAI(
                base_url=config.base_url,
                api_key=config.api_key,
                http_client=http_client,
                max_retries=0,  # Handle retries at higher level
            )
            
            logger.debug(f"Created optimized client for {config.base_url}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to create optimized client: {e}")
            raise ValueError(f"Invalid configuration: {e}")
    
    def _cleanup_client(self, client_key: str):
        """Clean up client reference when it's garbage collected."""
        if client_key in self._clients:
            logger.debug(f"Cleaning up client reference: {client_key}")
            del self._clients[client_key]
        if client_key in self._client_refs:
            del self._client_refs[client_key]
    
    async def close_all(self):
        """Close all clients and clean up resources."""
        async with self._lock:
            logger.info("Closing all HTTP clients and connections")
            await self._exit_stack.aclose()
            self._clients.clear()
            self._client_refs.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """Get pool statistics."""
        return {
            "active_clients": len(self._clients),
            "client_refs": len(self._client_refs)
        }


# Global client pool instance
_client_pool: Optional[ClientPool] = None
_pool_lock = asyncio.Lock()


async def get_client_pool() -> ClientPool:
    """Get or create the global client pool."""
    global _client_pool
    
    async with _pool_lock:
        if _client_pool is None:
            _client_pool = ClientPool()
            logger.info("Initialized global HTTP client pool")
        return _client_pool


async def get_or_create_client(config: LLMConfig) -> AsyncOpenAI:
    """
    Get an existing client or create a new one with connection pooling.
    
    This is the recommended way to get clients as it provides:
    - Client reuse for same configurations
    - HTTP connection pooling
    - Automatic resource management
    
    Args:
        config: LLM configuration parameters
        
    Returns:
        AsyncOpenAI: Optimized client instance
        
    Raises:
        ValueError: If configuration is invalid
    """
    pool = await get_client_pool()
    return await pool.get_client(config)


async def close_all_clients():
    """Close all pooled clients and clean up resources."""
    global _client_pool
    
    if _client_pool is not None:
        await _client_pool.close_all()
        _client_pool = None
        logger.info("Closed all HTTP clients")


async def get_client_stats() -> Dict[str, int]:
    """Get statistics about the client pool."""
    pool = await get_client_pool()
    return pool.get_stats()
