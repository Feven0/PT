"""Base manager implementation."""
from typing import (
    Dict, Any, Optional, Set, List,
    TypeVar, Generic,TYPE_CHECKING
)
from enum import Enum
from datetime import datetime, timezone
from time import perf_counter
import asyncio

from core.types.components import HealthStatus, ComponentState, HealthStatusInfo
from core.base.component import BaseComponent

if TYPE_CHECKING:
    from core.logging import BackendLogger
    from core.telemetry.metrics import MetricsManager

T = TypeVar('T')

context_name = "manager"
class ResourcePoolState(str, Enum):
    """Resource pool states."""
    ACTIVE = "active"
    DRAINING = "draining"
    DRAINED = "drained"

class ResourcePool:
    """Resource pool implementation."""
    
    def __init__(self, name: str):
        self.name = name
        self.resources: Set[Any] = set()
        self.state = ResourcePoolState.ACTIVE
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = self.created_at

class BaseManager(BaseComponent, Generic[T]):
    """Base manager implementation."""
    
    def __init__(
        self,
        name: str,
        config: Any,
        logger: Optional['BackendLogger'] = None,
        metrics: Optional['MetricsManager'] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize base manager.
        
        Args:
            name: Manager name
            config: Manager configuration
            logger: Logger instance
            metrics: Metrics manager instance
            dependencies: Set of dependencies
        """
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies
        )

        self._managed_components: Dict[str, BaseComponent] = {}
        self._resource_pools: Dict[str, ResourcePool] = {}
        self._initialization_lock = asyncio.Lock()
        self._is_initialized = False
        
    async def initialize(self) -> None:
        """Initialize manager."""
        async with self._initialization_lock:
            if self._is_initialized:
                return
                
            try:
                # Initialize managed components
                for component in self._managed_components.values():
                    await component.initialize()
                    
                # Initialize resource pools
                for pool in self._resource_pools.values():
                    pool.state = ResourcePoolState.ACTIVE
                    
                # Initialize implementation
                await self._initialize_impl()
                
                self._is_initialized = True
                self.logger.info(
                    "manager_initialized",
                    manager=self.name,
                    context=context_name
                )
                
            except Exception as e:
                self.logger.error(
                    "manager_initialization_failed",
                    error=str(e),
                    manager=self.name,
                    context=context_name
                )
                raise
                
    async def start(self) -> None:
        """Start manager."""
        self.state = ComponentState.INITIALIZING
        self.update_state_metric(self.state)
        if not self._is_initialized:
            await self.initialize()
            
        self.state = ComponentState.INITIALIZED
        self.update_state_metric(self.state)

        try:
            self.state = ComponentState.STARTING
            self.update_state_metric(self.state)
            
            # Start managed components
            for component in self._managed_components.values():
                await component.start()                
            
            # Start implementation
            await self._start_impl()
            
            self.state = ComponentState.RUNNING
            self.update_state_metric(self.state)
            self.logger.info(
                "manager_started",
                manager=self.name,
                context=context_name
            )
            
        except Exception as e:
            self.logger.error(
                "manager_start_failed",
                error=str(e),
                manager=self.name,
                context=context_name
            )
            raise
            
    async def stop(self) -> None:
        """Stop manager."""
        try:
            start_time = perf_counter()

            # Update state
            self.state = ComponentState.STOPPING
            self.update_state_metric(self.state)

            # Stop implementation first
            await self._stop_impl()
            
            # Stop managed components
            for component in reversed(list(self._managed_components.values())):
                await component.stop()
                
            # Drain resource pools
            for pool in self._resource_pools.values():
                pool.state = ResourcePoolState.DRAINING
                pool.resources.clear()
                pool.state = ResourcePoolState.DRAINED
                
            self.state = ComponentState.STOPPED
            self.update_state_metric(self.state)

            duration = perf_counter() - start_time
            self.record_operation("stop", duration, "success")

            self.logger.info(
                "manager_stopped",
                manager=self.name,
                context=context_name
            )
            
        except Exception as e:
            self.logger.error(
                "manager_stop_failed",
                error=str(e),
                manager=self.name,
                context=context_name
            )
            raise
            
    async def check_health(self) -> HealthStatusInfo:
        """Check manager health."""
        try:
            # Check managed components
            component_health = {}
            for name, component in self._managed_components.items():
                component_health[name] = await component.check_health()
                
            # Check resource pools
            pool_health = {}
            for name, pool in self._resource_pools.items():
                pool_health[name] = {
                    "state": pool.state,
                    "resource_count": len(pool.resources)
                }
                
            # Check implementation
            await self._check_health_impl()
            
            # Update health status
            self._health_status.update(
                status=HealthStatus.HEALTHY if all(h.is_healthy for h in component_health.values()) else HealthStatus.UNHEALTHY,
                details={
                    "components": {
                        name: health.details
                        for name, health in component_health.items()
                    },
                    "resource_pools": pool_health,
                    "state": self.state,
                    "is_initialized": self._is_initialized
                }
            )
            
            return self._health_status
            
        except Exception as e:
            self.logger.error(
                "manager_health_check_failed",
                error=str(e),
                manager=self.name,
                context=context_name
            )
            self._health_status.update(
                status=HealthStatus.UNHEALTHY,
                details={
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            return self._health_status
            
    async def register_managed_component(
        self,
        component: BaseComponent
    ) -> None:
        """Register managed component.
        
        Args:
            component: Component to manage
        """
        if component.name in self._managed_components:
            raise ValueError(f"Component {component.name} already registered")
            
        self._managed_components[component.name] = component
        self.logger.debug(
            f"{component.name} registered",
            manager=self.name,
            context=context_name
        )
        
    async def unregister_managed_component(
        self,
        component_name: str
    ) -> Optional[BaseComponent]:
        """Unregister managed component.
        
        Args:
            component_name: Name of component to unregister
            
        Returns:
            Unregistered component if found
        """
        component = self._managed_components.pop(component_name, None)
        if component:
            self.logger.info(
                "component_unregistered",
                component=component_name,
                manager=self.name,
                context=context_name
            )
        return component
        
    async def get_managed_components(self) -> List[BaseComponent]:
        """Get managed components.
        
        Returns:
            List of managed components
        """
        return list(self._managed_components.values())
        
    async def create_resource_pool(self, name: str) -> ResourcePool:
        """Create resource pool.
        
        Args:
            name: Pool name
            
        Returns:
            Created resource pool
        """
        if name in self._resource_pools:
            raise ValueError(f"Resource pool {name} already exists")
            
        pool = ResourcePool(name)
        self._resource_pools[name] = pool
        
        self.logger.info(
            "resource_pool_created",
            pool=name,
            manager=self.name,
            context=context_name
        )
        return pool
        
    async def delete_resource_pool(self, name: str) -> Optional[ResourcePool]:
        """Delete resource pool.
        
        Args:
            name: Pool name
            
        Returns:
            Deleted pool if found
        """
        pool = self._resource_pools.pop(name, None)
        if pool:
            pool.state = ResourcePoolState.DRAINING
            pool.resources.clear()
            pool.state = ResourcePoolState.DRAINED
            
            self.logger.info(
                "resource_pool_deleted",
                pool=name,
                manager=self.name,
                context=context_name
            )
        return pool
        
    async def add_to_resource_pool(
        self,
        pool_name: str,
        resource: T
    ) -> None:
        """Add resource to pool.
        
        Args:
            pool_name: Pool name
            resource: Resource to add
        """
        pool = self._resource_pools.get(pool_name)
        if not pool:
            pool = await self.create_resource_pool(pool_name)
            
        if pool.state != ResourcePoolState.ACTIVE:
            raise ValueError(f"Resource pool {pool_name} is not active")
            
        pool.resources.add(resource)
        pool.updated_at = datetime.now(timezone.utc)
        
    async def remove_from_resource_pool(
        self,
        pool_name: str,
        resource: T
    ) -> None:
        """Remove resource from pool.
        
        Args:
            pool_name: Pool name
            resource: Resource to remove
        """
        pool = self._resource_pools.get(pool_name)
        if not pool:
            return
            
        pool.resources.discard(resource)
        pool.updated_at = datetime.now(timezone.utc)
        
    async def get_resource_pool(
        self,
        name: str
    ) -> Optional[ResourcePool]:
        """Get resource pool.
        
        Args:
            name: Pool name
            
        Returns:
            Resource pool if found
        """
        return self._resource_pools.get(name)
        
    async def get_resource_pools(self) -> List[ResourcePool]:
        """Get all resource pools.
        
        Returns:
            List of resource pools
        """
        return list(self._resource_pools.values())
        
    async def _initialize_impl(self) -> None:
        """Initialize implementation."""
        pass
        
    async def _start_impl(self) -> None:
        """Start implementation."""
        pass
        
    async def _stop_impl(self) -> None:
        """Stop implementation."""
        pass
        
    async def _check_health_impl(self) -> None:
        """Check implementation health."""
        pass 