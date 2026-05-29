"""In-memory cache provider implementation."""
from typing import Optional, Any, Dict, Union
from datetime import datetime, timezone
import asyncio
import json
from collections import OrderedDict, defaultdict
import heapq

from core.base.component import BaseComponent
from core.telemetry.metrics import MetricsManager
from core.config import AppConfig
from core.logging import BackendLogger
from core.types.cache import CacheProviderProtocol, CacheKey, CacheValue
from core.types.queue import QueueProviderProtocol
from core.cache.exceptions import (
    CacheOperationError,
    CacheCapacityError,
    QueueOperationError
)

class CacheEntry:
    """Cache entry with metadata."""
    
    def __init__(
        self,
        value: CacheValue,
        ttl: Optional[int] = None
    ):
        self.value = value
        self.ttl = ttl
        self.created_at = datetime.now(timezone.utc)
        self.last_accessed = self.created_at
        self.access_count = 0
        
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl is None:
            return False
        return (datetime.now(timezone.utc) - self.created_at).total_seconds() > self.ttl
        
    def access(self) -> None:
        """Update access metadata."""
        self.last_accessed = datetime.now(timezone.utc)
        self.access_count += 1

class DelayedMessage:
    """Delayed message with priority queue support."""
    
    def __init__(self, message: Any, ready_time: float):
        self.message = message
        self.ready_time = ready_time
        
    def __lt__(self, other):
        return self.ready_time < other.ready_time


class MemoryQueue:
    """In-memory queue implementation."""
    
    def __init__(self):
        self.queue = asyncio.Queue()
        self.delayed = []  # heap queue for delayed messages
        self._lock = asyncio.Lock()
        
    async def push(self, message: Any, delay: Optional[int] = None) -> None:
        """Push message to queue."""
        if delay:
            ready_time = datetime.now().timestamp() + delay
            delayed_msg = DelayedMessage(message, ready_time)
            async with self._lock:
                heapq.heappush(self.delayed, delayed_msg)
        else:
            await self.queue.put(message)
            
    async def pop(self, timeout: Optional[int] = None) -> Optional[Any]:
        """Pop message from queue."""
        # First check and move any ready delayed messages
        await self._process_delayed()
        
        try:
            if timeout:
                return await asyncio.wait_for(self.queue.get(), timeout)
            else:
                if self.queue.empty():
                    return None
                return await self.queue.get()
        except asyncio.TimeoutError:
            return None
            
    async def _process_delayed(self) -> None:
        """Process delayed messages that are ready."""
        now = datetime.now().timestamp()
        
        async with self._lock:
            while self.delayed and self.delayed[0].ready_time <= now:
                delayed_msg = heapq.heappop(self.delayed)
                await self.queue.put(delayed_msg.message)
                
    async def length(self) -> int:
        """Get queue length."""
        async with self._lock:
            return self.queue.qsize() + len(self.delayed)
            
    async def clear(self) -> None:
        """Clear queue."""
        async with self._lock:
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            self.delayed.clear()


class MemoryCacheProvider(BaseComponent, 
                          CacheProviderProtocol, 
                          QueueProviderProtocol):
    """In-memory cache provider implementation."""
    
    def __init__(
        self,
        name: str,
        config: Union[AppConfig, Dict[str, Any]],
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None
    ):
        """Initialize memory cache provider."""
        super().__init__(
            name=name, 
            config=config, 
            metrics=metrics, 
            logger=logger
        )

        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._queues: Dict[str, MemoryQueue] = defaultdict(MemoryQueue)
        self._lock = asyncio.Lock()
        self._max_size = self._config.get("max_size", 1000)
        self._cleanup_task: Optional[asyncio.Task] = None

    async def _initialize_impl(self) -> None:
        """Initialize memory cache."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.logger.info(
            "memory_cache_initialized",
            context="cache",
            max_size=self._max_size
        )
        
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
            async with self._lock:
                entry = self._cache.get(key)
                if entry and not entry.is_expired():
                    entry.access()
                    # Move to end for LRU
                    self._cache.move_to_end(key)
                    return entry.value
                elif entry:
                    # Remove expired entry
                    del self._cache[key]
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
            CacheCapacityError: If cache is full
        """
        try:
            async with self._lock:
                if len(self._cache) >= self._max_size and key not in self._cache:
                    # Evict oldest entry
                    self._cache.popitem(last=False)
                    
                self._cache[key] = CacheEntry(value, ttl)
                # Move to end for LRU
                self._cache.move_to_end(key)
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
            async with self._lock:
                if key in self._cache:
                    del self._cache[key]
        except Exception as e:
            raise CacheOperationError(f"Failed to delete key {key}: {e}")
            
    async def exists(self, key: str) -> bool:
        """Check if key exists.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and not expired
            
        Raises:
            CacheOperationError: If operation fails
        """
        try:
            async with self._lock:
                entry = self._cache.get(key)
                if entry and not entry.is_expired():
                    return True
                elif entry:
                    # Remove expired entry
                    del self._cache[key]
        except Exception as e:
            raise CacheOperationError(f"Failed to check key {key}: {e}")
            
        return False
        
    async def clear(self) -> None:
        """Clear all cache entries.
        
        Raises:
            CacheOperationError: If operation fails
        """
        try:
            async with self._lock:
                self._cache.clear()
        except Exception as e:
            raise CacheOperationError(f"Failed to clear cache: {e}")
            
    async def _cleanup_loop(self) -> None:
        """Background task to clean up expired entries."""
        while True:
            try:
                async with self._lock:
                    # Create list of expired keys
                    expired = [
                        key for key, entry in self._cache.items()
                        if entry.is_expired()
                    ]
                    # Remove expired entries
                    for key in expired:
                        del self._cache[key]
                        
                    if expired:
                        self.logger.debug(
                            "expired_entries_cleaned",
                            context="cache",
                            count=len(expired)
                        )
            except Exception as e:
                self.logger.error(
                    "cleanup_error",
                    context="cache",
                    error=str(e)
                )
                
            await asyncio.sleep(60)  # Run every minute
            
    async def cleanup(self) -> None:
        """Clean up resources."""
        # Clear all queues
        for queue in self._queues.values():
            await queue.clear()
        self._queues.clear()
        
        # Clean up cache
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            
        async with self._lock:
            self._cache.clear()

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
            await self._queues[queue].push(message, delay)
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
            return await self._queues[queue].pop(timeout)
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
            return await self._queues[queue].length()
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
            await self._queues[queue].clear()
        except Exception as e:
            raise QueueOperationError(f"Failed to clear queue {queue}: {e}") 