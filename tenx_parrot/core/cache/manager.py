"""Cache manager implementation."""
from typing import Dict, Any, Optional, Set, TYPE_CHECKING, TypeVar, Generic, Union
from datetime import datetime
import asyncio

if TYPE_CHECKING:
    from core.telemetry.metrics import MetricsManager
    from core.logging import BackendLogger

from core.base.manager import BaseManager
from core.config import AppConfig, CacheConfig
from core.types.components import ComponentState, HealthStatus
from core.types.cache import (
    CacheProviderProtocol,
    CacheKey,
    CacheValue,
    CacheDict
)
from core.types.queue import QueueProviderProtocol
from .providers import PROVIDERS

from .exceptions import (
    CacheProviderError,
    CacheOperationError,
    CacheConnectionError,
    QueueOperationError
)

class CacheManager(BaseManager):
    """Cache manager implementation."""
    
    def __init__(
        self,
        name: str,
        config: Union[Dict[str, Any], 'AppConfig'],
        metrics: Optional['MetricsManager'] = None,
        logger: Optional['BackendLogger'] = None,
        dependencies: Optional[Dict[str, Any]] = None
    ):
        """Initialize cache manager."""
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies
        )

        self._provider: Optional[Union[CacheProviderProtocol, QueueProviderProtocol]] = None
        self._provider_name = self._config.get("provider", "memory")
        
        # Initialize cache client based on config
        self._client = None
        self._ttl = self._config.get("ttl", 3600)
        self._max_size = self._config.get("max_size", 1000)
        self._cleanup_interval = self._config.get("cleanup_interval", 300)
        
        # Update health status with cache specific details
        self._health_status.details.update({
            "provider": self._provider_name,
            "ttl": self._ttl,
            "max_size": self._max_size,
            "cleanup_interval": self._cleanup_interval,
            "enabled": self._config.get("enabled", False)
        })

    async def _initialize_impl(self) -> None:
        """Initialize cache manager."""
        if not self._config.get("enabled", False):
            self.logger.warning("Cache manager disabled by configuration")
            return

        try:
            # Get provider class
            provider_class = PROVIDERS.get(self._provider_name)
            if not provider_class:
                raise CacheProviderError(f"Unknown cache provider: {self._provider_name}")
                
            # Create provider instance with cache-specific config
            self._provider = provider_class(
                name=f"{self.name}_provider",
                config=self._config,  # BaseManager already processed this to be cache config
                metrics=self.metrics,
                logger=self.logger
            )
            
            # Initialize provider
            await self._provider.initialize()
            
            # Register queue metrics if provider supports it
            if isinstance(self._provider, QueueProviderProtocol):
                self._register_queue_metrics()
            
            self.logger.info(
                "cache_manager_initialized",
                context="cache",
                provider=self._provider_name
            )
            
        except Exception as e:
            raise CacheConnectionError(f"Failed to initialize cache manager: {e}")

    def _register_queue_metrics(self) -> None:
        """Register queue-specific metrics."""
        if not self.metrics:
            return
            
        
        self.metrics.register_metric(
            f"{self.name}_queue_operations_total",
            "counter",
            "Total number of queue operations",
            labels={"operation": "", "queue": "", "status": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_queue_messages",
            "gauge",
            "Current number of messages in queue",
            labels={"queue": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_queue_operation_duration_seconds",
            "histogram",
            "Duration of queue operations",
            labels={"operation": "", "queue": ""}
        )

    async def get(self, key: CacheKey) -> Optional[CacheValue]:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found
            
        Raises:
            CacheOperationError: If operation fails
        """
        if not self._provider:
            raise CacheProviderError("Cache provider not initialized")
            
        try:
            with self.metrics.timer("cache_get", {"provider": self._provider_name}):
                return await self._provider.get(key)
        except Exception as e:
            self.logger.error(
                "cache_get_failed",
                context="cache",
                key=key,
                error=str(e)
            )
            raise CacheOperationError(f"Failed to get key {key}: {e}")
            
    async def set(
        self,
        key: CacheKey,
        value: CacheValue,
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
        if not self._provider:
            raise CacheProviderError("Cache provider not initialized")
            
        try:
            with self.metrics.timer("cache_set", {"provider": self._provider_name}):
                await self._provider.set(key, value, ttl)
        except Exception as e:
            self.logger.error(
                "cache_set_failed",
                context="cache",
                key=key,
                error=str(e)
            )
            raise CacheOperationError(f"Failed to set key {key}: {e}")
            
    async def delete(self, key: CacheKey) -> None:
        """Delete cache key.
        
        Args:
            key: Cache key
            
        Raises:
            CacheOperationError: If operation fails
        """
        if not self._provider:
            raise CacheProviderError("Cache provider not initialized")
            
        try:
            with self.metrics.timer("cache_delete", {"provider": self._provider_name}):
                await self._provider.delete(key)
        except Exception as e:
            self.logger.error(
                "cache_delete_failed",
                context="cache",
                key=key,
                error=str(e)
            )
            raise CacheOperationError(f"Failed to delete key {key}: {e}")
            
    async def exists(self, key: CacheKey) -> bool:
        """Check if key exists.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists
            
        Raises:
            CacheOperationError: If operation fails
        """
        if not self._provider:
            raise CacheProviderError("Cache provider not initialized")
            
        try:
            with self.metrics.timer("cache_exists", {"provider": self._provider_name}):
                return await self._provider.exists(key)
        except Exception as e:
            self.logger.error(
                "cache_exists_failed",
                context="cache",
                key=key,
                error=str(e)
            )
            raise CacheOperationError(f"Failed to check key {key}: {e}")
            
    async def clear(self) -> None:
        """Clear all cache entries.
        
        Raises:
            CacheOperationError: If operation fails
        """
        if not self._provider:
            return
            
        try:
            with self.metrics.timer("cache_clear", {"provider": self._provider_name}):
                await self._provider.clear()
        except Exception as e:
            self.logger.error(
                "cache_clear_failed",
                context="cache",
                error=str(e)
            )
            raise CacheOperationError("Failed to clear cache: {e}")
            
    async def cleanup(self) -> None:
        """Clean up resources."""
        if self._provider:
            await self._provider.cleanup()
            self._provider = None 

    async def _cleanup_impl(self) -> None:
        """Clean up cache resources."""
        try:
            # Clear all caches
            await self.clear()
            
            # Close provider connection
            if self._provider:
                await self._provider.cleanup()
                self._provider = None
                
            if self.logger:
                self.logger.info(
                    "cache_manager_cleaned_up",
                    manager=self.name
                )
                
        except Exception as e:
            if self.logger:
                self.logger.error(
                    "cache_cleanup_failed",
                    error=str(e),
                    manager=self.name
                )
            raise 

    async def queue_push(
        self, 
        queue: str, 
        message: Any, 
        delay: Optional[int] = None
    ) -> None:
        """Push message to queue."""
        if not isinstance(self._provider, QueueProviderProtocol):
            raise QueueOperationError("Provider does not support queue operations")
            
        try:
            with self.metrics.timer("queue_push", {"provider": self._provider_name}):
                await self._provider.queue_push(queue, message, delay)
        except Exception as e:
            self.logger.error(
                "queue_push_failed",
                context="queue",
                queue=queue,
                error=str(e)
            )
            raise QueueOperationError(f"Failed to push to queue {queue}: {e}")

    async def queue_pop(
        self, 
        queue: str, 
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Pop message from queue."""
        if not isinstance(self._provider, QueueProviderProtocol):
            raise QueueOperationError("Provider does not support queue operations")
            
        try:
            with self.metrics.timer("queue_pop", {"provider": self._provider_name}):
                return await self._provider.queue_pop(queue, timeout)
        except Exception as e:
            self.logger.error(
                "queue_pop_failed",
                context="queue",
                queue=queue,
                error=str(e)
            )
            raise QueueOperationError(f"Failed to pop from queue {queue}: {e}")

    async def queue_length(self, queue: str) -> int:
        """Get queue length."""
        if not isinstance(self._provider, QueueProviderProtocol):
            raise QueueOperationError("Provider does not support queue operations")
            
        try:
            with self.metrics.timer("queue_length", {"provider": self._provider_name}):
                return await self._provider.queue_length(queue)
        except Exception as e:
            self.logger.error(
                "queue_length_failed",
                context="queue",
                queue=queue,
                error=str(e)
            )
            raise QueueOperationError(f"Failed to get queue length for {queue}: {e}")

    async def queue_clear(self, queue: str) -> None:
        """Clear queue."""
        if not isinstance(self._provider, QueueProviderProtocol):
            raise QueueOperationError("Provider does not support queue operations")
            
        try:
            with self.metrics.timer("queue_clear", {"provider": self._provider_name}):
                await self._provider.queue_clear(queue)
        except Exception as e:
            self.logger.error(
                "queue_clear_failed",
                context="queue",
                queue=queue,
                error=str(e)
            )
            raise QueueOperationError(f"Failed to clear queue {queue}: {e}") 