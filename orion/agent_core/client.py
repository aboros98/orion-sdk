"""
HTTP client management for agent_core.

This module provides a unified client pool for managing both synchronous and 
asynchronous OpenAI API connections with connection pooling and reuse.
"""

from openai import AsyncOpenAI, OpenAI
from .config import LLMConfig
from typing import Dict, Optional, Union
import asyncio
import logging
import weakref
import httpx
from contextlib import AsyncExitStack, ExitStack
import threading

logger = logging.getLogger(__name__)


def _get_client_key(config: LLMConfig) -> str:
    """Generate a unique key for client identification."""
    return f"{config.base_url}:{config.api_key[:8]}..."


def _get_optimized_http_limits() -> httpx.Limits:
    """Get optimized HTTP connection limits."""
    return httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20,
        keepalive_expiry=30.0
    )


def _get_optimized_http_timeout() -> httpx.Timeout:
    """Get optimized HTTP timeout settings."""
    return httpx.Timeout(
        connect=10.0,
        read=60.0,
        write=10.0,
        pool=5.0
    )


class ClientPool:
    """
    Unified client pool that manages both async and sync OpenAI clients.
    
    Features:
    - Client reuse based on configuration
    - HTTP connection pooling 
    - Automatic cleanup of unused clients
    - Thread-safe access for both async and sync operations
    - Unified interface for both client types
    """
    
    def __init__(self):
        # Async clients storage
        self._async_clients: Dict[str, AsyncOpenAI] = {}
        self._async_client_refs: Dict[str, weakref.ref] = {}
        self._async_lock = asyncio.Lock()
        self._async_exit_stack = AsyncExitStack()
        
        # Sync clients storage
        self._sync_clients: Dict[str, OpenAI] = {}
        self._sync_client_refs: Dict[str, weakref.ref] = {}
        self._sync_lock = threading.Lock()
        self._sync_exit_stack = ExitStack()
    
    # ASYNC METHODS
    
    async def get_async_client(self, config: LLMConfig) -> AsyncOpenAI:
        """
        Get or create an async client for the given configuration.
        
        Args:
            config: LLM configuration
            
        Returns:
            AsyncOpenAI: Reused or newly created async client
        """
        client_key = _get_client_key(config)
        
        async with self._async_lock:
            # Check if we have a valid client
            if client_key in self._async_clients:
                client = self._async_clients[client_key]
                if client is not None:
                    logger.debug(f"Reusing existing async client for key: {client_key}")
                    return client
            
            # Create new client with optimized settings
            logger.info(f"Creating new optimized async client for key: {client_key}")
            client = await self._create_optimized_async_client(config)
            
            # Store client and set up cleanup
            self._async_clients[client_key] = client
            self._async_client_refs[client_key] = weakref.ref(
                client, 
                lambda ref: self._cleanup_async_client(client_key)
            )
            
            return client
    
    async def _create_optimized_async_client(self, config: LLMConfig) -> AsyncOpenAI:
        """Create a new AsyncOpenAI client with optimized HTTP settings."""
        
        # Create optimized HTTP client with connection pooling
        http_client = httpx.AsyncClient(
            limits=_get_optimized_http_limits(),
            timeout=_get_optimized_http_timeout(),
            follow_redirects=True,
            http2=True  # Enable HTTP/2 if available
        )
        
        # Register for cleanup
        await self._async_exit_stack.enter_async_context(http_client)
        
        try:
            client = AsyncOpenAI(
                base_url=config.base_url,
                api_key=config.api_key,
                http_client=http_client,
                max_retries=0,  # Handle retries at higher level
            )
            
            logger.debug(f"Created optimized async client for {config.base_url}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to create optimized async client: {e}")
            raise ValueError(f"Invalid configuration: {e}")
    
    def _cleanup_async_client(self, client_key: str):
        """Clean up async client reference when it's garbage collected."""
        if client_key in self._async_clients:
            del self._async_clients[client_key]
        if client_key in self._async_client_refs:
            del self._async_client_refs[client_key]
        logger.debug(f"Cleaned up async client: {client_key}")
    
    async def close_all_async(self):
        """Close all async clients and clean up resources."""
        async with self._async_lock:
            logger.info("Closing all async HTTP clients and connections")
            await self._async_exit_stack.aclose()
            self._async_clients.clear()
            self._async_client_refs.clear()
    
    # SYNC METHODS
    
    def get_sync_client(self, config: LLMConfig) -> OpenAI:
        """
        Get or create a sync client for the given configuration.
        
        Args:
            config: LLM configuration
            
        Returns:
            OpenAI: Reused or newly created sync client
        """
        client_key = _get_client_key(config)
        
        with self._sync_lock:
            # Check if we have a valid client
            if client_key in self._sync_clients:
                client = self._sync_clients[client_key]
                if client is not None:
                    logger.debug(f"Reusing existing sync client for key: {client_key}")
                    return client
            
            # Create new client with optimized settings
            logger.info(f"Creating new optimized sync client for key: {client_key}")
            client = self._create_optimized_sync_client(config)
            
            # Store client and set up cleanup
            self._sync_clients[client_key] = client
            self._sync_client_refs[client_key] = weakref.ref(
                client, 
                lambda ref: self._cleanup_sync_client(client_key)
            )
            
            return client
    
    def _create_optimized_sync_client(self, config: LLMConfig) -> OpenAI:
        """Create a new OpenAI client with optimized HTTP settings."""
        
        # Create optimized HTTP client with connection pooling
        http_client = httpx.Client(
            limits=_get_optimized_http_limits(),
            timeout=_get_optimized_http_timeout(),
            follow_redirects=True,
            http2=True  # Enable HTTP/2 if available
        )
        
        # Register for cleanup
        self._sync_exit_stack.enter_context(http_client)
        
        try:
            client = OpenAI(
                base_url=config.base_url,
                api_key=config.api_key,
                http_client=http_client,
                max_retries=0,  # Handle retries at higher level
            )
            
            logger.debug(f"Created optimized sync client for {config.base_url}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to create optimized sync client: {e}")
            raise ValueError(f"Invalid configuration: {e}")
    
    def _cleanup_sync_client(self, client_key: str):
        """Clean up sync client reference when it's garbage collected."""
        if client_key in self._sync_clients:
            del self._sync_clients[client_key]
        if client_key in self._sync_client_refs:
            del self._sync_client_refs[client_key]
        logger.debug(f"Cleaned up sync client: {client_key}")
    
    def close_all_sync(self):
        """Close all sync clients and clean up resources."""
        with self._sync_lock:
            logger.info("Closing all sync HTTP clients and connections")
            self._sync_exit_stack.close()
            self._sync_clients.clear()
            self._sync_client_refs.clear()
    
    # UNIFIED METHODS
    
    def get_stats(self) -> Dict[str, int]:
        """Get pool statistics for both async and sync clients."""
        return {
            "async_clients": len(self._async_clients),
            "async_client_refs": len(self._async_client_refs),
            "sync_clients": len(self._sync_clients),
            "sync_client_refs": len(self._sync_client_refs),
            "total_clients": len(self._async_clients) + len(self._sync_clients),
        }
    
    async def close_all(self):
        """Close all clients (both async and sync) and clean up resources."""
        await self.close_all_async()
        self.close_all_sync()
    
    # BACKWARD COMPATIBILITY METHODS
    
    async def get_client(self, config: LLMConfig) -> AsyncOpenAI:
        """Backward compatibility: get async client."""
        return await self.get_async_client(config)


# GLOBAL POOL

_client_pool: Optional[ClientPool] = None
_pool_lock = threading.Lock()  # Use threading.Lock for sync safety


def get_client_pool() -> ClientPool:
    """Get or create the global unified client pool."""
    global _client_pool
    
    with _pool_lock:
        if _client_pool is None:
            _client_pool = ClientPool()
            logger.info("Initialized global unified client pool")
        return _client_pool


# ASYNC CONVENIENCE FUNCTIONS

async def get_or_create_client(config: LLMConfig) -> AsyncOpenAI:
    """
    Get an existing async client or create a new one with connection pooling.
    
    This is the recommended way to get async clients as it provides:
    - Client reuse for same configurations
    - HTTP connection pooling
    - Automatic resource management
    
    Args:
        config: LLM configuration parameters
        
    Returns:
        AsyncOpenAI: Optimized async client instance
        
    Raises:
        ValueError: If configuration is invalid
    """
    pool = get_client_pool()
    return await pool.get_async_client(config)


async def close_all_clients():
    """Close all pooled clients and clean up resources."""
    global _client_pool
    
    if _client_pool is not None:
        await _client_pool.close_all()
        _client_pool = None
        logger.info("Closed all HTTP clients")


async def get_client_stats() -> Dict[str, int]:
    """Get statistics about the client pool."""
    pool = get_client_pool()
    return pool.get_stats()


# SYNC CONVENIENCE FUNCTIONS

def get_or_create_sync_client(config: LLMConfig) -> OpenAI:
    """
    Get an existing sync client or create a new one with connection pooling.
    
    This is the recommended way to get sync clients as it provides:
    - Client reuse for same configurations
    - HTTP connection pooling
    - Automatic resource management
    
    Args:
        config: LLM configuration parameters
        
    Returns:
        OpenAI: Optimized sync client instance
        
    Raises:
        ValueError: If configuration is invalid
    """
    pool = get_client_pool()
    return pool.get_sync_client(config)


def close_all_sync_clients():
    """Close all pooled sync clients and clean up resources."""
    pool = get_client_pool()
    pool.close_all_sync()
    logger.info("Closed all sync HTTP clients")


def get_sync_client_stats() -> Dict[str, int]:
    """Get statistics about the sync client pool."""
    pool = get_client_pool()
    return pool.get_stats()


# BACKWARD COMPATIBILITY ALIASES

# These maintain the old interface for existing code
SyncClientPool = ClientPool  # Alias for backward compatibility

def get_sync_client_pool() -> ClientPool:
    """Backward compatibility: get the unified client pool."""
    return get_client_pool()

async def get_client_pool_async() -> ClientPool:
    """Backward compatibility: get the unified client pool (async version)."""
    return get_client_pool() 