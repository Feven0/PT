"""Core resilience patterns.

This module provides resilience patterns for handling failures and managing load:
- Retry with exponential backoff
- Rate limiting
- Circuit breaking
- Connection pooling
"""

from .retry import RetryWithBackoff, RetryManager, retry
from .rate_limiter import RateLimiter
from .circuit_breaker import (
    CircuitBreaker,
    circuit_breaker,
    timeout
)
from .connection_pool import ConnectionPool

__all__ = [
    # Core implementations
    "RetryWithBackoff",
    "RetryManager",
    "RateLimiter",
    "CircuitBreaker",
    "ConnectionPool",
    
    # Decorators and utilities
    "retry",
    "circuit_breaker",
    "timeout"
] 