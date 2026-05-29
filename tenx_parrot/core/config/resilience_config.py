"""Resilience configuration."""
from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator
from enum import Enum

from core.types.model import CoreBaseModel


class RetryConfig(CoreBaseModel):
    """Retry configuration."""
    enabled: bool = Field(default=True, description="Enable retry mechanism")
    max_retries: int = Field(default=3, ge=1, description="Maximum number of retries")
    initial_delay: float = Field(default=1.0, ge=0.1, description="Initial delay in seconds")
    max_delay: float = Field(default=30.0, ge=1.0, description="Maximum delay in seconds")
    exponential_base: float = Field(default=2.0, ge=1.0, description="Exponential backoff base")
    jitter: bool = Field(default=True, description="Add jitter to delays")
    retry_on_exceptions: List[str] = Field(
        default=[
            "ConnectionError",
            "TimeoutError",
            "RequestError",
            "ServiceUnavailable"
        ],
        description="Exception types to retry on"
    )

    # @field_validator("max_delay")
    # def validate_max_delay(cls, v, values):
    #     """Validate max delay is greater than initial delay."""
    #     if "initial_delay" in values and v < values["initial_delay"]:
    #         return values["initial_delay"] * 10
    #     return v

class RetryPolicy(CoreBaseModel):
    """Retry policy configuration."""
    policies: Dict[str, RetryConfig] = Field(default_factory=dict, description="List of retry policies")

class RateLimiterConfig(CoreBaseModel):
    """Rate limiter configuration."""
    enabled: bool = Field(default=True, description="Enable rate limiting")
    max_calls: int = Field(default=100, ge=1, description="Maximum calls per time window")
    time_window: float = Field(default=60.0, ge=1.0, description="Time window in seconds")
    strategy: str = Field(default="fixed_window", description="Rate limiting strategy")
    distributed: bool = Field(default=False, description="Use distributed rate limiting")
    fallback_enabled: bool = Field(default=True, description="Enable fallback on errors")
    burst_size: int = Field(default=10, ge=1, le=1000, description="Maximum burst size")

    # @field_validator("burst_size")
    # def validate_burst_size(cls, v, values):
    #     """Validate burst size is not larger than max_calls."""
    #     if "max_calls" in values and v > values["max_calls"]:
    #         return values["max_calls"]
    #     return v

class CircuitBreakerConfig(CoreBaseModel):
    """Circuit breaker configuration."""
    name: str = Field(default="default", description="Circuit breaker name")
    enabled: bool = Field(default=True, description="Enable circuit breaker")
    failure_threshold: int = Field(default=5, description="Number of failures before opening")
    success_threshold: int = Field(default=3, description="Number of successes before closing")
    timeout: float = Field(default=30.0, description="Open state timeout in seconds")
    half_open_timeout: float = Field(default=15.0, description="Half-open state timeout")
    window_size: int = Field(default=10, description="Rolling window size")
    monitored_exceptions: List[str] = Field(
        default=[
            "ConnectionError",
            "TimeoutError",
            "RequestError",
            "ServiceUnavailable"
        ],
        description="Exception types to monitor"
    )
    exclude_exceptions: List[str] = Field(
        default=[
            "ValidationError",
            "AuthenticationError",
            "PermissionError"
        ],
        description="Exception types to exclude"
    )

class BulkheadConfig(CoreBaseModel):
    """Bulkhead configuration."""
    enabled: bool = Field(default=True, description="Enable bulkhead")
    max_concurrent_calls: int = Field(default=10, description="Maximum concurrent calls")
    max_queue_size: int = Field(default=20, description="Maximum queue size")
    queue_timeout: float = Field(default=5.0, description="Queue timeout in seconds")
    fairness: bool = Field(default=True, description="Enable fair scheduling")

class TimeoutConfig(CoreBaseModel):
    """Timeout configuration."""
    enabled: bool = Field(default=True, description="Enable timeout")
    default_timeout: float = Field(default=30.0, description="Default timeout in seconds")
    cancel_on_timeout: bool = Field(default=True, description="Cancel operation on timeout")
    operation_timeouts: Dict[str, float] = Field(
        default={
            "database": 10.0,
            "http": 30.0,
            "storage": 60.0,
            "compute": 120.0
        },
        description="Operation-specific timeouts"
    )

class FallbackConfig(CoreBaseModel):
    """Fallback configuration."""
    enabled: bool = Field(default=True, description="Enable fallback")
    max_fallback_attempts: int = Field(default=3, ge=1, description="Maximum fallback attempts")
    fallback_timeout: float = Field(default=5.0, ge=0.5, description="Fallback timeout in seconds")
    fallback_strategies: List[str] = Field(
        default=["retry", "circuit_breaker", "timeout"],
        description="Fallback strategy order"
    )

    @field_validator("fallback_strategies")
    def validate_strategies(cls, v):
        """Ensure at least one strategy is specified."""
        if not v:
            return ["retry"]  # Default to retry if empty
        return v

class RecoveryConfig(CoreBaseModel):
    """Recovery configuration."""
    enabled: bool = Field(default=True, description="Enable recovery mechanism")
    cleanup_interval: int = Field(default=300, ge=60, description="Cleanup interval in seconds")
    attempt_expiry: int = Field(default=3600, ge=300, description="Time in seconds after which recovery attempts expire")
    cooldown_period: int = Field(default=300, ge=60, description="Cooldown period between recovery attempts in seconds")
    thresholds: Dict[str, int] = Field(
        default={
            "service": 3,
            "connection": 5, 
            "storage": 3
        },
        description="Recovery attempt thresholds by component type"
    )
    default_threshold: int = Field(default=3, ge=1, description="Default recovery attempt threshold")
    log_level: str = Field(default="WARNING", description="Recovery log level")

    # @field_validator("thresholds")
    # def validate_thresholds(cls, v):
    #     """Validate threshold values."""
    #     if not all(threshold >= 1 for threshold in v.values()):
    #         raise ValueError("All threshold values must be >= 1")
    #     return v

    # @field_validator("log_level")
    # def validate_log_level(cls, v):
    #     """Validate log level."""
    #     valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    #     if v.upper() not in valid_levels:
    #         raise ValueError(f"Log level must be one of {valid_levels}")
    #     return v.upper()

class ResilienceConfig(CoreBaseModel):
    """Resilience configuration."""
    enabled: bool = Field(default=True, description="Enable resilience mechanisms")
    metrics_enabled: bool = Field(default=True, description="Enable resilience metrics")
    retry: RetryConfig = Field(default_factory=RetryConfig)
    rate_limiter: RateLimiterConfig = Field(default_factory=RateLimiterConfig)
    circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig)
    bulkhead: BulkheadConfig = Field(default_factory=BulkheadConfig)
    timeout: TimeoutConfig = Field(default_factory=TimeoutConfig)
    fallback: FallbackConfig = Field(default_factory=FallbackConfig)
    recovery: RecoveryConfig = Field(default_factory=RecoveryConfig)
    log_failures: bool = Field(default=True, description="Log resilience failures")
    alert_on_degraded: bool = Field(default=True, description="Alert on degraded state") 