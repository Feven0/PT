"""Rate limiter implementation."""
from typing import (
    Dict, Any, List, Set, 
    Optional, Callable, 
    TypeVar, Generic, 
    TYPE_CHECKING, Union
)
from datetime import datetime, timezone, timedelta
import asyncio
from enum import Enum
from functools import wraps

if TYPE_CHECKING:
    from core.telemetry.metrics import MetricsManager
    from core.logging import BackendLogger

from core.base.manager import BaseManager
from core.types.metrics import MetricsProtocol, MetricType
from core.types.protocols import ComponentProtocol, LoggerProtocol
from core.config import AppConfig, RateLimiterConfig
from core.types.base import ComponentState
from core.types.components import HealthStatus, HealthStatusInfo
from core.types.resilience import RateLimitStrategy, BaseRateLimiter

K = TypeVar('K')
T = TypeVar('T')


class RateLimiter(BaseRateLimiter[K]):
    """Default rate limiter implementation."""
    
    def __init__(
        self,
        name: str,
        config: Optional[RateLimiterConfig] = None,
        metrics: Optional[MetricsProtocol] = None,
        logger: Optional[LoggerProtocol] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize rate limiter.
        
        Args:
            name: Rate limiter name
            config: Optional rate limiter configuration
            metrics: Optional metrics manager
            logger: Optional logger instance
            dependencies: Optional dependencies
        """
        self.name = name
        self.config = config or RateLimiterConfig()
        self._logger = logger
        self._metrics = metrics
        self._dependencies = dependencies or set()
        self._state = ComponentState.CREATED
        
        # Initialize rate limiter state
        self.strategy = self.config.strategy
        self.tokens = self.config.max_calls
        self.tokens_per_interval = self.config.max_calls
        self.interval_seconds = self.config.time_window
        self.burst_size = self.config.burst_size or self.tokens_per_interval
        self.last_update = datetime.now(timezone.utc)
        self.total_requests = 0
        self.allowed_requests = 0
        self.rejected_requests = 0

        if metrics:
            self._register_metrics()

    async def initialize(self) -> None:
        """Initialize component."""
        self._state = ComponentState.INITIALIZED

    async def start(self) -> None:
        """Start component."""
        self._state = ComponentState.RUNNING

    async def stop(self) -> None:
        """Stop component."""
        self._state = ComponentState.STOPPED

    async def check_health(self) -> HealthStatusInfo:
        """Check rate limiter health.
        
        Returns:
            Health status information
        """
        try:
            # Calculate recent statistics
            now = datetime.now(timezone.utc)
            recent_window = timedelta(minutes=5)  # Last 5 minutes
            
            # Calculate request rates
            total_rate = self.total_requests / self.interval_seconds if self.interval_seconds > 0 else 0
            allowed_rate = self.allowed_requests / self.interval_seconds if self.interval_seconds > 0 else 0
            rejected_rate = self.rejected_requests / self.interval_seconds if self.interval_seconds > 0 else 0
            
            # Determine health status
            if self._state != ComponentState.RUNNING:
                status = HealthStatus.UNHEALTHY
            elif self.rejected_requests == 0:
                status = HealthStatus.HEALTHY
            elif rejected_rate > (total_rate * 0.5):  # More than 50% rejection rate
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
                
            # Update health status
            self._health_status.update(
                status=status,
                details={
                    "total_requests": self.total_requests,
                    "allowed_requests": self.allowed_requests,
                    "rejected_requests": self.rejected_requests,
                    "current_tokens": self.tokens,
                    "request_rates": {
                        "total": total_rate,
                        "allowed": allowed_rate,
                        "rejected": rejected_rate
                    },
                    "configuration": {
                        "strategy": self.strategy,
                        "tokens_per_interval": self.tokens_per_interval,
                        "interval_seconds": self.interval_seconds,
                        "burst_size": self.burst_size
                    },
                    "last_update": self.last_update.isoformat(),
                    "state": self._state
                }
            )
            
            return self._health_status
            
        except Exception as e:
            self._health_status.update(
                status=HealthStatus.UNHEALTHY,
                details={
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            return self._health_status
        
    def _replenish_tokens(self) -> None:
        """Replenish tokens based on elapsed time."""
        now = datetime.now(timezone.utc)
        elapsed = (now - self.last_update).total_seconds()
        
        if elapsed >= self.interval_seconds:
            self.tokens = min(
                self.burst_size,
                self.tokens + int(elapsed * self.tokens_per_interval / self.interval_seconds)
            )
            self.last_update = now
            
    async def acquire(self, key: K, tokens: int = 1) -> bool:
        """Acquire tokens.
        
        Args:
            key: Request key
            tokens: Number of tokens to acquire
            
        Returns:
            True if tokens were acquired
        """
        self.total_requests += 1
        
        if self.strategy == RateLimitStrategy.TOKEN_BUCKET:
            self._replenish_tokens()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                self.allowed_requests += 1
                return True
                
            self.rejected_requests += 1
            return False
            
        elif self.strategy == RateLimitStrategy.FIXED_WINDOW:
            now = datetime.now(timezone.utc)
            elapsed = (now - self.last_update).total_seconds()
            
            if elapsed >= self.interval_seconds:
                self.tokens = self.tokens_per_interval
                self.last_update = now
                
            if self.tokens >= tokens:
                self.tokens -= tokens
                self.allowed_requests += 1
                return True
                
            self.rejected_requests += 1
            return False
            
        elif self.strategy == RateLimitStrategy.SLIDING_WINDOW:
            now = datetime.now(timezone.utc)
            elapsed = (now - self.last_update).total_seconds()
            
            # Calculate tokens based on sliding window
            if elapsed < self.interval_seconds:
                remaining_ratio = 1 - (elapsed / self.interval_seconds)
                self.tokens = min(
                    self.burst_size,
                    int(self.tokens * remaining_ratio) + self.tokens_per_interval
                )
            else:
                self.tokens = self.tokens_per_interval
                
            self.last_update = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                self.allowed_requests += 1
                return True
                
            self.rejected_requests += 1
            return False
            
        return False

    def _register_metrics(self) -> None:
        """Register rate limiter metrics."""
        self._metrics.register_metric(
            f"{self.name}_current_tokens",
            MetricType.GAUGE,
            f"Current number of tokens in {self.name}",
            labels={"strategy": ""}
        )
        
        self._metrics.register_metric(
            f"{self.name}_requests_total",
            MetricType.COUNTER,
            f"Total number of requests in {self.name}",
            labels={"status": "", "strategy": ""}
        )
        
        self._metrics.register_metric(
            f"{self.name}_rejected_requests_total",
            MetricType.COUNTER,
            f"Total number of rejected requests in {self.name}",
            labels={"strategy": ""}
        )
        
        self._metrics.register_metric(
            f"{self.name}_request_latency_seconds",
            MetricType.HISTOGRAM,
            f"Request latency in seconds in {self.name}",
            labels={"strategy": "", "status": ""}
        )

class RateLimiterManager(BaseManager[RateLimiter[Any]]):
    """Rate limiter manager implementation."""
    
    def __init__(
        self,
        name: str,
        config: Union[Dict[str, Any], 'AppConfig'],
        metrics: Optional['MetricsManager'] = None,
        cache: Optional[Any] = None,
        dependencies: Optional[Set[str]] = None
    ) -> None:
        """Initialize rate limiter manager.
        
        Args:
            name: Rate limiter manager name
            config: Rate limiter configuration or AppConfig
            metrics: Optional metrics manager
            cache: Optional cache provider
            dependencies: Optional dependencies
        """
        # Initialize with required dependencies
        required_deps = {"metrics", "cache"}
        if dependencies:
            required_deps.update(dependencies)
                    
        super().__init__(name=name, 
                         config=config, 
                         metrics=metrics, 
                         dependencies=dependencies)
        
        # Initialize rate limiter settings from config
        self._max_requests = self._config.get("max_requests", 100)
        self._time_window = self._config.get("time_window", 60.0)
        self._burst_size = self._config.get("burst_size", 10)
        self._algorithm = self._config.get("algorithm", "token_bucket")
        
        # Update health status with rate limiter specific details
        self._health_status.details.update({
            "max_requests": self._max_requests,
            "time_window": self._time_window,
            "burst_size": self._burst_size,
            "algorithm": self._algorithm
        })
        
        self._limiters: Dict[str, RateLimiter[Any]] = {}
        self._monitor_task: Optional[asyncio.Task] = None
        self._monitor_interval = 10  # seconds
        self._cache = cache
        
    async def _initialize_impl(self) -> None:
        """Initialize rate limiter manager."""
        await super()._initialize_impl()
        
        self._limiters.clear()
        
        # Get cache provider
        if "cache" in self.dependencies:
            try:
                self._cache = await self._get_dependency("cache")
                self.logger.info(
                    "cache_initialized",
                    manager=self.name
                )
            except Exception as e:
                self.logger.error(
                    "cache_init_failed",
                    error=str(e),
                    manager=self.name
                )
                self._cache = None
        
        # Register metrics
        if self.metrics:
            self.metrics.register_metric(
                name=f"{self.name}_limiters_total",
                type="gauge",
                description=f"Total number of rate limiters",
                labels={"strategy": ""}
            )
            self.metrics.register_metric(
                name=f"{self.name}_requests_total",
                type="counter",
                description=f"Total number of rate limiter requests",
                labels={"limiter": "", "status": ""}
            )
            self.metrics.register_metric(
                name=f"{self.name}_tokens_remaining",
                type=MetricType.GAUGE,
                description=f"Number of tokens remaining in {self.name}",
                component=self.name
            )
            self.metrics.register_metric(
                name=f"{self.name}_check_duration_seconds",
                type=MetricType.HISTOGRAM,
                description=f"Duration of rate limit checks in {self.name}",
                component=self.name
            )
            
        # Initialize state store integration
        if "state_store" in self.dependencies:
            try:
                stored_limiters = await self._state_store.get_rate_limiters()
                for name, limiter_data in stored_limiters.items():
                    await self.create_limiter(
                        name=name,
                        tokens_per_interval=limiter_data["tokens_per_interval"],
                        interval_seconds=limiter_data["interval_seconds"],
                        strategy=RateLimitStrategy(limiter_data.get("strategy", "token_bucket")),
                        burst_size=limiter_data.get("burst_size")
                    )
            except Exception as e:
                self.logger.error(
                    "state_store_load_failed",
                    error=str(e),
                    manager=self.name
                )
                
    async def _save_state(self, name: str, limiter: RateLimiter[Any]) -> None:
        """Save limiter state to store."""
        if "state_store" not in self.dependencies:
            return
            
        try:
            await self._state_store.save_rate_limiter(
                name,
                {
                    "tokens_per_interval": limiter.tokens_per_interval,
                    "interval_seconds": limiter.interval_seconds,
                    "strategy": limiter.strategy,
                    "burst_size": limiter.burst_size,
                    "tokens": limiter.tokens,
                    "last_update": limiter.last_update,
                    "total_requests": limiter.total_requests,
                    "allowed_requests": limiter.allowed_requests,
                    "rejected_requests": limiter.rejected_requests
                }
            )
        except Exception as e:
            self.logger.error(
                "state_store_save_failed",
                error=str(e),
                limiter=name
            )
            
    async def create_limiter(
        self,
        name: str,
        tokens_per_interval: Optional[int] = None,
        interval_seconds: Optional[float] = None,
        strategy: Optional[RateLimitStrategy] = None,
        burst_size: Optional[int] = None
    ) -> RateLimiter[Any]:
        """Create rate limiter.
        
        Args:
            name: Rate limiter name
            tokens_per_interval: Optional number of tokens per interval (defaults to config)
            interval_seconds: Optional interval in seconds (defaults to config)
            strategy: Optional rate limiting strategy (defaults to config)
            burst_size: Optional burst size (defaults to config)
            
        Returns:
            Rate limiter instance
        """
        # Create config for this limiter
        config = RateLimiterConfig(
            max_calls=tokens_per_interval or self.config.max_calls,
            time_window=interval_seconds or self.config.time_window,
            strategy=strategy or self.config.strategy,
            burst_size=burst_size or self.config.burst_size
        )
        
        limiter = RateLimiter(
            name=name,
            config=config,
            metrics=self.metrics,
            logger=self.logger,
            dependencies=self._dependencies
        )
        
        self._limiters[name] = limiter
        await self._save_state(name, limiter)
        
        if self.metrics:
            self.metrics.record(
                name=f"{self.name}_limiters_total",
                value=float(len(self._limiters)),
                labels={"strategy": limiter.strategy}
            )
            
        return limiter
        
    async def get_limiter(self, name: str) -> Optional[RateLimiter[Any]]:
        """Get rate limiter.
        
        Args:
            name: Rate limiter name
            
        Returns:
            Rate limiter if found
        """
        return self._limiters.get(name)
        
    async def delete_limiter(self, name: str) -> None:
        """Delete rate limiter.
        
        Args:
            name: Rate limiter name
        """
        limiter = self._limiters.pop(name, None)
        if limiter:
            if "state_store" in self.dependencies:
                try:
                    await self._state_store.delete_rate_limiter(name)
                except Exception as e:
                    self.logger.error(
                        "state_store_delete_failed",
                        error=str(e),
                        limiter=name
                    )
                    
            if self.metrics:
                self.metrics.record(
                    name=f"{self.name}_limiters_total",
                    value=float(len(self._limiters)),
                    labels={"strategy": limiter.strategy}
                )
                
    async def check_rate_limit(
        self,
        name: str,
        key: Any,
        tokens: int = 1
    ) -> bool:
        """Check rate limit.
        
        Args:
            name: Rate limiter name
            key: Request key
            tokens: Number of tokens to acquire
            
        Returns:
            True if request is allowed
        """
        start_time = datetime.now(timezone.utc)
        
        # Try cache first if available
        if self._cache:
            try:
                # Use cache for atomic operations
                cache_key = f"rate_limit:{name}:{key}"
                tokens_key = f"{cache_key}:tokens"
                timestamp_key = f"{cache_key}:timestamp"
                
                # Get current tokens and timestamp
                async with self._cache.pipeline() as pipe:
                    current_tokens = await self._cache.get(tokens_key)
                    last_update = await self._cache.get(timestamp_key)
                    
                    current_tokens = int(current_tokens) if current_tokens else self.config.burst_size
                    last_update = float(last_update) if last_update else 0
                    
                    # Calculate token replenishment
                    now = datetime.now(timezone.utc).timestamp()
                    elapsed = now - last_update
                    
                    if elapsed >= self.config.interval_seconds:
                        current_tokens = self.config.tokens_per_interval
                    else:
                        current_tokens = min(
                            self.config.burst_size,
                            current_tokens + int(elapsed * self.config.tokens_per_interval / self.config.interval_seconds)
                        )
                    
                    # Check if we have enough tokens
                    if current_tokens >= tokens:
                        # Update tokens and timestamp atomically
                        await self._cache.set(tokens_key, current_tokens - tokens)
                        await self._cache.set(timestamp_key, now)
                        
                        if self.metrics:
                            self.metrics.record(
                                name=f"{self.name}_requests_total",
                                value=1.0,
                                labels={"limiter": name, "status": "allowed"}
                            )
                        return True
                    
                    if self.metrics:
                        self.metrics.record(
                            name=f"{self.name}_requests_total",
                            value=1.0,
                            labels={"limiter": name, "status": "rejected"}
                        )
                    return False
                    
            except Exception as e:
                self.logger.error(
                    "cache_rate_limit_failed",
                    error=str(e),
                    limiter=name,
                    key=str(key)
                )
                # Fallback to memory limiter
        
        # Use memory limiter as fallback
        limiter = await self.get_limiter(name)
        if not limiter:
            if self.metrics:
                self.metrics.record(
                    name=f"{self.name}_requests_total",
                    value=1.0,
                    labels={"limiter": name, "status": "not_found"}
                )
            return True
            
        allowed = await limiter.acquire(key, tokens)
        end_time = datetime.now(timezone.utc)
        
        if self.metrics:
            duration = (end_time - start_time).total_seconds()
            status = "allowed" if allowed else "rejected"
            
            self.metrics.record(
                name=f"{self.name}_requests_total",
                value=1.0,
                labels={"limiter": name, "status": status}
            )
            self.metrics.record(
                name=f"{self.name}_tokens_remaining",
                value=float(limiter.tokens),
                labels={"limiter": name}
            )
            self.metrics.record(
                name=f"{self.name}_check_duration_seconds",
                value=duration,
                labels={"limiter": name, "status": status}
            )
            
        await self._save_state(name, limiter)
        return allowed
        
    async def _monitor_limiters(self) -> None:
        """Monitor rate limiters."""
        while True:
            try:
                for name, limiter in self._limiters.items():
                    # Update metrics
                    if self.metrics:
                        self.metrics.record(
                            name=f"{self.name}_tokens_remaining",
                            value=float(limiter.tokens),
                            labels={"limiter": name}
                        )
                        
                    # Save state
                    await self._save_state(name, limiter)
                    
                await asyncio.sleep(self._monitor_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(
                    "limiter_monitor_failed",
                    error=str(e),
                    manager=self.name
                )
                await asyncio.sleep(60)  # Retry after 1 minute 



def rate_limit(
    name: str,
    tokens_per_interval: Optional[int] = None,
    interval_seconds: Optional[float] = None,
    strategy: Optional[RateLimitStrategy] = None,
    burst_size: Optional[int] = None,
    key_func: Optional[Callable[..., Any]] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Rate limit decorator.
    
    Args:
        name: Rate limiter name
        tokens_per_interval: Optional number of tokens per interval (defaults to config)
        interval_seconds: Optional interval in seconds (defaults to config)
        strategy: Optional rate limiting strategy (defaults to config)
        burst_size: Optional burst size (defaults to config)
        key_func: Optional function to generate key from function arguments
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            
            # Get rate limiter manager from container
            manager = await RateLimiterManager.create_limiter(*args, **kwargs)
            
            # Create or get rate limiter
            limiter = await manager.get_limiter(name)
            if not limiter:
                limiter = await manager.create_limiter(
                    name=name,
                    tokens_per_interval=tokens_per_interval,
                    interval_seconds=interval_seconds,
                    strategy=strategy,
                    burst_size=burst_size
                )
            
            # Generate key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                # Default to function name if no key function
                key = func.__name__
            
            # Check rate limit
            if not await limiter.acquire(key):
                raise RateLimitExceeded(
                    f"Rate limit exceeded for {name} with key {key}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    pass 