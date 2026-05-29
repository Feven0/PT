"""Cache providers."""
from typing import Dict, Type

from core.types.cache import CacheProviderProtocol
from .redis import RedisCacheProvider
from .memory import MemoryCacheProvider
from core.cache.exceptions import CacheProviderError

PROVIDERS: Dict[str, Type[CacheProviderProtocol]] = {
    "redis": RedisCacheProvider,
    "memory": MemoryCacheProvider
}

__all__ = [
    "PROVIDERS",
    "RedisCacheProvider",
    "MemoryCacheProvider",
    "CacheProviderError"
] 