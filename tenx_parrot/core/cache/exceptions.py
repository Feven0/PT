"""Cache exceptions."""

class CacheError(Exception):
    """Base class for cache errors."""
    pass

class CacheConnectionError(CacheError):
    """Raised when cache connection fails."""
    pass

class CacheOperationError(CacheError):
    """Raised when cache operation fails."""
    pass

class CacheConfigError(CacheError):
    """Raised when cache configuration is invalid."""
    pass

class CacheProviderError(CacheError):
    """Raised when cache provider operation fails."""
    pass

class CacheKeyError(CacheError):
    """Raised when cache key is invalid or not found."""
    pass

class CacheValueError(CacheError):
    """Raised when cache value is invalid."""
    pass

class CacheTimeoutError(CacheError):
    """Raised when cache operation times out."""
    pass

class CacheCapacityError(CacheError):
    """Raised when cache capacity is exceeded."""
    pass 

class QueueOperationError(CacheError):
    """Raised when cache capacity is exceeded."""
    pass 