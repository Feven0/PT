"""Cache type definitions."""
from typing import Any, Optional, Protocol, Dict, Union, runtime_checkable, List
from datetime import datetime

from core.types.base import InfrastructureProviderProtocol

CacheKey = str
CacheValue = Any
CacheDict = Dict[CacheKey, CacheValue]

class CacheProviderProtocol(Protocol):
    """Cache provider protocol."""
    
    async def get(self, key: CacheKey) -> Optional[CacheValue]:
        """Get value from cache."""
        ...
    
    async def set(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: Optional[int] = None
    ) -> None:
        """Set cache value."""
        ...
    
    async def delete(self, key: CacheKey) -> None:
        """Delete cache key."""
        ...
    
    async def exists(self, key: CacheKey) -> bool:
        """Check if key exists."""
        ...
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        ...
    
    async def get_batch(
        self,
        keys: List[CacheKey]
    ) -> Dict[CacheKey, Optional[CacheValue]]:
        """Get multiple values from cache."""
        ...
    
    async def set_batch(
        self,
        items: Dict[CacheKey, CacheValue],
        ttl: Optional[int] = None
    ) -> None:
        """Set multiple cache values."""
        ...
    
    async def delete_batch(
        self,
        keys: List[CacheKey]
    ) -> None:
        """Delete multiple cache keys."""
        ...
    
    async def get_ttl(self, key: CacheKey) -> Optional[int]:
        """Get TTL for a cache key in seconds."""
        ...
    
    async def set_ttl(self, key: CacheKey, ttl: int) -> bool:
        """Set TTL for a cache key in seconds."""
        ...
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        ... 