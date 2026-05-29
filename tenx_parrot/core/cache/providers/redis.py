"""Redis cache provider implementation."""
from typing import Dict, Any, Optional, Set, TYPE_CHECKING, TypeVar, Generic
from datetime import datetime
import asyncio
import json
import redis.asyncio as redis
from redis.asyncio.client import Redis

if TYPE_CHECKING:
    from core.telemetry.metrics import MetricsManager
    from core.logging import BackendLogger
    from core.resilience.retry import RetryManager
    from core.resilience.circuit_breaker import CircuitBreaker


from core.base.component import BaseComponent
from core.config import AppConfig, RedisConfig
from core.types.base import ComponentState
from core.types.components import HealthStatus
from core.types.cache import CacheProviderProtocol, CacheKey, CacheValue
from core.types.queue import QueueProviderProtocol
from core.cache.exceptions import (
    CacheConnectionError,
    CacheOperationError,
    CacheProviderError,
    QueueOperationError
)

class RedisCacheProvider(BaseComponent, 
                         CacheProviderProtocol, 
                         QueueProviderProtocol):
    """Redis cache provider implementation."""
    
    def __init__(
        self,
        name: str,
        config: Any,
        metrics: Optional['MetricsManager'] = None,
        logger: Optional['BackendLogger'] = None,
        retry: Optional['RetryManager'] = None,
        circuit_breaker: Optional['CircuitBreaker'] = None
    ):
        """Initialize Redis cache provider.
        
        Args:
            name: Provider name
            config: Application configuration
            metrics: Optional metrics manager
            logger: Optional logger instance
            retry: Optional retry manager
            circuit_breaker: Optional circuit breaker
        """

        """Initialize memory cache provider."""
        super().__init__(
            name=name, 
            config=config, 
            metrics=metrics, 
            logger=logger
        )
        self.retry = retry
        self.circuit_breaker = circuit_breaker
        self._client: Optional[Redis] = None

        
    async def _initialize_impl(self) -> None:
        """Initialize Redis connection."""
        try:
            # Check if URL is provided in config
            if self._config.get("url"):
                self._client = redis.Redis.from_url(
                    self._config["url"],
                    db=self._config.get("db", 0),
                    ssl=self._config.get("ssl", False),
                    decode_responses=True
                )
            else:
                # Fall back to individual parameters
                self._client = redis.Redis(
                    host=self._config.get("host", "localhost"),
                    port=self._config.get("port", 6379),
                    db=self._config.get("db", 0),
                    password=self._config.get("password", None),
                    ssl=self._config.get("ssl", False),
                    decode_responses=True
                )
            
            await self._client.ping()
            self.logger.info(
                "redis_cache_initialized",
                context="cache",
                host=self._config.get("host", "localhost"),
                port=self._config.get("port", 6379)
            )
        except Exception as e:
            raise CacheConnectionError(f"Failed to connect to Redis: {e}")
            
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found
            
        Raises:
            CacheOperationError: If operation fails
        """
        try:
            value = await self._client.get(key)
            if value:
                return value
        except Exception as e:
            raise CacheOperationError(f"Failed to get key {key}: {e}")
            
        return None
        
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """Set cache value.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL in seconds
            
        Raises:
            CacheOperationError: If operation fails
        """
        try:
            await self._client.set(
                key,
                value,
                ex=ttl
            )
        except Exception as e:
            raise CacheOperationError(f"Failed to set key {key}: {e}")
            
    async def delete(self, key: str) -> None:
        """Delete cache key.
        
        Args:
            key: Cache key
            
        Raises:
            CacheOperationError: If operation fails
        """
        try:
            await self._client.delete(key)
        except Exception as e:
            raise CacheOperationError(f"Failed to delete key {key}: {e}")
            
    async def exists(self, key: str) -> bool:
        """Check if key exists.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists
            
        Raises:
            CacheOperationError: If operation fails
        """
        try:
            return await self._client.exists(key) > 0
        except Exception as e:
            raise CacheOperationError(f"Failed to check key {key}: {e}")
            
    async def clear(self) -> None:
        """Clear all cache entries.
        
        Raises:
            CacheOperationError: If operation fails
        """
        try:
            await self._client.flushdb()
        except Exception as e:
            raise CacheOperationError(f"Failed to clear cache: {e}")
            
    async def cleanup(self) -> None:
        """Clean up resources."""
        if self._client:
            await self._client.close()
            self._client = None 

    async def queue_push(
        self, 
        queue: str, 
        message: Any, 
        delay: Optional[int] = None
    ) -> None:
        """Push message to queue.
        
        Args:
            queue: Queue name
            message: Message to push
            delay: Optional delay in seconds
            
        Raises:
            QueueOperationError: If operation fails
        """
        try:
            # Serialize message
            serialized = json.dumps(message)
            
            if delay:
                # Use sorted set for delayed messages
                score = datetime.now().timestamp() + delay
                await self._client.zadd(f"{queue}:delayed", {serialized: score})
            else:
                # Use list for immediate messages
                await self._client.lpush(queue, serialized)
                
        except Exception as e:
            raise QueueOperationError(f"Failed to push to queue {queue}: {e}")

    async def queue_pop(
        self, 
        queue: str, 
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Pop message from queue.
        
        Args:
            queue: Queue name
            timeout: Optional timeout in seconds
            
        Returns:
            Message if available, None if queue empty
            
        Raises:
            QueueOperationError: If operation fails
        """
        try:
            # First check delayed messages
            now = datetime.now().timestamp()
            delayed_queue = f"{queue}:delayed"
            
            # Move ready delayed messages to main queue
            ready = await self._client.zrangebyscore(
                delayed_queue, 
                0, 
                now
            )
            if ready:
                # Remove from delayed set and add to main queue
                await self._client.zremrangebyscore(delayed_queue, 0, now)
                await self._client.rpush(queue, *ready)
            
            # Pop from main queue
            if timeout:
                result = await self._client.brpop(queue, timeout=timeout)
                if result:
                    _, message = result
                else:
                    return None
            else:
                message = await self._client.rpop(queue)
                if not message:
                    return None
                    
            return json.loads(message)
            
        except Exception as e:
            raise QueueOperationError(f"Failed to pop from queue {queue}: {e}")

    async def queue_length(self, queue: str) -> int:
        """Get queue length.
        
        Args:
            queue: Queue name
            
        Returns:
            Number of messages in queue
            
        Raises:
            QueueOperationError: If operation fails
        """
        try:
            # Get length of main queue
            main_len = await self._client.llen(queue)
            
            # Get length of delayed queue
            delayed_len = await self._client.zcard(f"{queue}:delayed")
            
            return main_len + delayed_len
            
        except Exception as e:
            raise QueueOperationError(f"Failed to get queue length for {queue}: {e}")

    async def queue_clear(self, queue: str) -> None:
        """Clear queue.
        
        Args:
            queue: Queue name
            
        Raises:
            QueueOperationError: If operation fails
        """
        try:
            # Clear main queue
            await self._client.delete(queue)
            
            # Clear delayed queue
            await self._client.delete(f"{queue}:delayed")
            
        except Exception as e:
            raise QueueOperationError(f"Failed to clear queue {queue}: {e}") 