"""Lifecycle registry for managing component lifecycles."""
from typing import Dict, Optional, Any, Set, List
from datetime import datetime, timezone
import asyncio
from collections import defaultdict

from core.logging import BackendLogger
from core.config import AppConfig
from .lifecycle import LifecycleAware, ComponentState
from core.types.components import (
    HealthStatus,
    HealthStatusInfo,
    ComponentStateInfo
)

logger = BackendLogger(name="lifecycle").get_logger()


class DependencyError(Exception):
    """Error raised when there are dependency issues."""
    pass


class LifecycleRegistry:
    """Registry for managing component lifecycles."""
    
    def __init__(self, config: Optional[AppConfig] = None):
        """Initialize lifecycle registry.
        
        Args:
            config: Optional application configuration
        """
        self.config = config
        self.components: Dict[str, LifecycleAware] = {}
        self.health_status: Dict[str, HealthStatusInfo] = {}
        self.start_times: Dict[str, datetime] = {}
        self._dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self._reverse_deps: Dict[str, Set[str]] = defaultdict(set)
        self._initialization_lock = asyncio.Lock()
        self.initialized = False
        
        # Registry's own health status
        self._health_status = HealthStatusInfo(
            status=HealthStatus.UNKNOWN,
            details={
                "component": "lifecycle_registry",
                "initialized": False,
                "component_count": 0,
                "healthy_components": 0,
                "unhealthy_components": 0
            },
            state_info=ComponentStateInfo(
                state=ComponentState.CREATED,
                transition_time=datetime.now(timezone.utc)
            )
        )
        
    def register(self, name: str, component: LifecycleAware) -> None:
        """Register a component for lifecycle management.
        
        Args:
            name: Component name
            component: Component instance
        """
        if name in self.components:
            logger.warning(
                "component_already_registered",
                context="lifecycle",
                component=name
            )
            return
            
        self.components[name] = component
        self.health_status[name] = component.health_status
        
        # Register dependencies
        for dep in component.dependencies:
            self._dependency_graph[name].add(dep)
            self._reverse_deps[dep].add(name)
            
        # Update registry health status
        self._update_registry_health()
            
        logger.info(
            f"{name} registered",
            context="lifecycle"
        )
        #dependencies=list(component.dependencies)
        
    def _update_registry_health(self) -> None:
        """Update registry's health status based on components."""
        total_components = len(self.components)
        healthy_components = 0
        unhealthy_components = 0
        degraded_components = 0
        
        for status in self.health_status.values():
            if not isinstance(status, HealthStatusInfo):
                status = HealthStatusInfo(**status)
            if status.status == HealthStatus.HEALTHY:
                healthy_components += 1
            elif status.status == HealthStatus.UNHEALTHY:
                unhealthy_components += 1
            elif status.status == HealthStatus.DEGRADED:
                degraded_components += 1
            
        
        # Determine overall status
        if not self.components:
            status = HealthStatus.UNKNOWN
        elif unhealthy_components > 0:
            status = HealthStatus.UNHEALTHY
        elif degraded_components > 0:
            status = HealthStatus.DEGRADED
        elif healthy_components == total_components:
            status = HealthStatus.HEALTHY
        else:
            status = HealthStatus.DEGRADED
            
        self._health_status.update(
            status=status,
            details={
                **self._health_status.details,
                "component_count": total_components,
                "healthy_components": healthy_components,
                "unhealthy_components": unhealthy_components,
                "degraded_components": degraded_components,
                "initialized": self.initialized,
                "last_update": datetime.now(timezone.utc).isoformat()
            }
        )
        
    def _get_initialization_order(self) -> List[str]:
        """Get component initialization order based on dependencies.
        
        Returns:
            List of component names in initialization order
        
        Raises:
            DependencyError: If there are circular dependencies
        """
        visited = set()
        temp_mark = set()
        order = []
        
        def visit(name: str):
            if name in temp_mark:
                raise DependencyError(f"Circular dependency detected involving {name}")
            if name in visited:
                return
                
            temp_mark.add(name)
            
            # Visit all dependencies first
            for dep in self._dependency_graph[name]:
                if dep not in self.components:
                    raise DependencyError(f"Missing dependency {dep} for component {name}")
                visit(dep)
                
            temp_mark.remove(name)
            visited.add(name)
            order.append(name)
            
        # Visit all components
        for name in self.components:
            if name not in visited:
                visit(name)
                
        return order
        
    async def initialize(self) -> None:
        """Initialize all registered components in dependency order."""
        async with self._initialization_lock:
            if self.initialized:
                logger.warning(
                    "registry_already_initialized",
                    context="lifecycle"
                )
                return
                
            # logger.info(
            #     "initializing_components",
            #     context="lifecycle",
            #     json_data={
            #         "Components": list(self.components.keys())
            #     }
            # )
            
            try:
                # Get initialization order
                init_order = self._get_initialization_order()
                
                # Initialize components in order
                for name in init_order:
                    component = self.components[name]
                    try:
                        await component.initialize()
                        self.health_status[name] = await component.check_health()
                        logger.info(
                            "component_initialized",
                            context="lifecycle",
                            component=name
                        )
                    except Exception as e:
                        logger.error(
                            "component_init_failed",
                            context="lifecycle",
                            component=name,
                            error=str(e)
                        )
                        raise
                        
                self.initialized = True
                self._update_registry_health()
                
            except Exception as e:
                logger.error(
                    "initialization_failed",
                    context="lifecycle",
                    error=str(e)
                )
                raise
                
    async def start(self) -> None:
        """Start all registered components in dependency order."""
        if not self.initialized:
            logger.warning(
                "registry_not_initialized",
                context="lifecycle"
            )
            await self.initialize()
            
        # logger.info(
        #     "starting_components",
        #     context="lifecycle",
        #     json_data={
        #         "Components": list(self.components.keys())
        #     }
        # )
        
        # Start in same order as initialization
        init_order = self._get_initialization_order()
        
        for name in init_order:
            component = self.components[name]
            try:
                await component.start()
                self.start_times[name] = datetime.now(timezone.utc)
                self.health_status[name] = await component.check_health()
                logger.info(
                    "component_started",
                    context="lifecycle",
                    component=name
                )
            except Exception as e:
                logger.error(
                    "component_start_failed",
                    context="lifecycle",
                    component=name,
                    error=str(e)
                )
                raise
                
        self._update_registry_health()
                
    async def stop(self) -> None:
        """Stop all registered components in reverse dependency order."""
        # logger.info(
        #     "stopping_components",
        #     context="lifecycle",
        #     json_data={
        #         "Components": list(self.components.keys())
        #     }
        # )
        # Stop in reverse order of initialization
        stop_order = reversed(self._get_initialization_order())
        
        for name in stop_order:
            component = self.components[name]
            try:
                # Add timeout for each component stop
                await asyncio.wait_for(
                    component.stop(),
                    timeout=5.0  # 5 second timeout per component
                )
                self.health_status[name] = await component.check_health()
                logger.info(
                    "component_stopped",
                    context="lifecycle",
                    component=name
                )
            except asyncio.TimeoutError:
                logger.error(
                    "component_stop_timeout",
                    context="lifecycle",
                    component=name,
                    error="Operation timed out"
                )
            except Exception as e:
                logger.error(
                    "component_stop_failed",
                    context="lifecycle",
                    component=name,
                    error=str(e)
                )
                # Continue stopping other components
                
        self.initialized = False
        self._update_registry_health()
        
    async def check_health(self, component_name: Optional[str] = None) -> Dict[str, Any]:
        """Get health status of components.
        
        Args:
            component_name: Optional component name to get status for
            
        Returns:
            Health status information
        """
        if component_name:
            if component_name not in self.components:
                return {
                    "status": HealthStatus.UNKNOWN.value,
                    "message": "Component not found"
                }
                
            component = self.components[component_name]
            status = await component.check_health()
            self.health_status[component_name] = status
            
            result = {
                "status": status.status.value,
                "uptime": (datetime.now(timezone.utc) - self.start_times.get(component_name, datetime.now(timezone.utc))).total_seconds() if component.state == ComponentState.RUNNING else 0,
                "details": status.details,
                "state_info": status.state_info.model_dump() if status.state_info else None,
                "last_check": status.timestamp.isoformat(),
                "state": component.state.value,
                "dependencies": list(component.dependencies)
            }
            
            self._update_registry_health()
            return result
            
        # Check all components
        results = {}
        for name, component in self.components.items():
            status = await component.check_health()
            self.health_status[name] = status
            
            results[name] = {
                "status": status.status.value,
                "uptime": (datetime.now(timezone.utc) - self.start_times.get(name, datetime.now(timezone.utc))).total_seconds() if component.state == ComponentState.RUNNING else 0,
                "details": status.details,
                "state_info": status.state_info.model_dump() if status.state_info else None,
                "last_check": status.timestamp.isoformat(),
                "state": component.state.value,
                "dependencies": list(component.dependencies)
            }
            
        self._update_registry_health()
        
        # Include registry's own health status
        results["registry"] = self._health_status.model_dump()
        
        return results
        
    def get_dependencies(self, component_name: str) -> Set[str]:
        """Get dependencies for a component.
        
        Args:
            component_name: Component name
            
        Returns:
            Set of dependency names
        """
        return self._dependency_graph[component_name].copy()
        
    def get_dependents(self, component_name: str) -> Set[str]:
        """Get components that depend on this component.
        
        Args:
            component_name: Component name
            
        Returns:
            Set of dependent component names
        """
        return self._reverse_deps[component_name].copy()
        
    async def cleanup(self) -> None:
        """Clean up all registered components."""
        # logger.info(
        #     "cleaning_up_components",
        #     context="lifecycle",
        #     json_data={
        #         "Components": list(self.components.keys())
        #     }
        # )
        
        # Stop all components first if not already stopped
        if self.initialized:
            await self.stop()
        
        # Clean up components in reverse order
        cleanup_order = reversed(self._get_initialization_order())
        for name in cleanup_order:
            try:
                component = self.components[name]
                if hasattr(component, 'cleanup'):
                    try:
                        # Add timeout for each component cleanup
                        if asyncio.iscoroutinefunction(component.cleanup):
                            await asyncio.wait_for(
                                component.cleanup(),
                                timeout=5.0  # 5 second timeout per component
                            )
                        else:
                            component.cleanup()
                        logger.info(
                            "component_cleaned_up",
                            context="lifecycle",
                            component=name
                        )
                    except asyncio.TimeoutError:
                        logger.error(
                            "component_cleanup_timeout",
                            context="lifecycle",
                            component=name
                        )
                    except Exception as e:
                        logger.error(
                            "component_cleanup_failed",
                            context="lifecycle",
                            component=name,
                            error=str(e)
                        )
            except Exception as e:
                logger.error(
                    "component_cleanup_error",
                    context="lifecycle",
                    component=name,
                    error=str(e)
                )
        
        # Clear all registrations
        self.components.clear()
        self.health_status.clear()
        self.start_times.clear()
        self._dependency_graph.clear()
        self._reverse_deps.clear()
        self.initialized = False
        
        # Update registry health status
        self._update_registry_health() 