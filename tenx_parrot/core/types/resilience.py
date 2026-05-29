"""Resilience-related type definitions."""

from enum import Enum
from typing import TypeVar, Dict, Any, Optional, Union, Set, Generic
from datetime import datetime, timezone
from pydantic import Field

from core.types.model import CoreBaseModel
from core.types.protocols import ComponentProtocol


K = TypeVar('K')

class RateLimitStrategy(str, Enum):
    """Rate limit strategies."""
    TOKEN_BUCKET = "token_bucket"  # Token bucket algorithm
    FIXED_WINDOW = "fixed_window"  # Fixed window counter
    SLIDING_WINDOW = "sliding_window"  # Sliding window counter

class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast
    HALF_OPEN = "half_open"  # Testing if service is healthy


class BaseRateLimiter(ComponentProtocol, Generic[K]):
    """Rate limiter protocol."""
    
    async def initialize(self) -> None:
        """Initialize rate limiter."""
        raise NotImplementedError()
        
    async def start(self) -> None:
        """Start rate limiter."""
        raise NotImplementedError()
        
    async def stop(self) -> None:
        """Stop rate limiter."""
        raise NotImplementedError()
        
    async def check_health(self) -> Dict[str, Any]:
        """Check rate limiter health."""
        raise NotImplementedError()
        
    async def acquire(self, key: K, tokens: int = 1) -> bool:
        """Acquire tokens."""
        raise NotImplementedError()