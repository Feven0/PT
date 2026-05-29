"""Connection pool implementation."""
from typing import Any, Optional, Set
from asyncio import Lock, Queue
from contextlib import asynccontextmanager

from core.telemetry.metrics import MetricsManager
from core.types.metrics import MetricType
class ConnectionPool:
    """Connection pool implementation."""
    
    def __init__(
        self,
        name: str,
        max_size: int,
        metrics: Optional[MetricsManager] = None
    ):
        """Initialize connection pool.
        
        Args:
            name: Pool name
            max_size: Maximum pool size
            metrics: Optional metrics collector
        """
        self._name = name
        self._max_size = max_size
        self._metrics = metrics or MetricsManager()
        self._pool: Queue[Any] = Queue(maxsize=max_size)
        self._active: Set[Any] = set()
        self._lock = Lock()
                      
    
        # Register metrics
        if self._metrics:
            self._metrics.register_metric(
                name=f"{self._name}_size",
                type=MetricType.GAUGE,
                description=f"Current size of {self._name} connection pool",
                component=self._name
            )
            self._metrics.register_metric(
                name=f"{self._name}_active",
                type=MetricType.GAUGE,
                description=f"Current number of active connections in {self._name} connection pool",
                component=self._name
            )
            self._metrics.register_metric(
                name=f"{self._name}_successes_total",
                type=MetricType.COUNTER,
                description=f"Total number of successes in {self._name}",
                component=self._name
            )
            self._metrics.register_metric(
                name=f"{self._name}_state_changes_total",
                type=MetricType.COUNTER,
                description=f"Total number of state changes in {self._name}",
                component=self._name
            ) 
            
    @property
    def size(self) -> int:
        """Get current pool size."""
        return self._pool.qsize()
        
    @property
    def active(self) -> int:
        """Get number of active connections."""
        return len(self._active)
        
    async def add(self, conn: Any) -> None:
        """Add connection to pool.
        
        Args:
            conn: Connection to add
        """
        await self._pool.put(conn)
        if self._metrics:
            self._metrics.gauge(
                "connection_pool_size",
                self.size,
                labels={"name": self._name}
            )
            
    async def remove(self, conn: Any) -> None:
        """Remove connection from pool.
        
        Args:
            conn: Connection to remove
        """
        async with self._lock:
            if conn in self._active:
                self._active.remove(conn)
                if self._metrics:
                    self._metrics.gauge(
                        "connection_pool_active",
                        self.active,
                        labels={"name": self._name}
                    )
                    
    @asynccontextmanager
    async def connection(self) -> Any:
        """Get connection from pool."""
        conn = await self._pool.get()
        try:
            async with self._lock:
                self._active.add(conn)
                if self._metrics:
                    self._metrics.gauge(
                        f"{self._name}_active",
                        self.active,
                        labels={"name": self._name}
                    )
            yield conn
        finally:
            async with self._lock:
                self._active.remove(conn)
                if self._metrics:
                    self._metrics.gauge(
                        f"{self._name}_active",
                        self.active,
                        labels={"name": self._name}
                    )
            await self._pool.put(conn) 