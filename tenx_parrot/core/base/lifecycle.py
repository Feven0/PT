"""Lifecycle management interface."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union
from datetime import datetime, timezone

from core.types.components import (
    HealthStatus,
    ComponentState,
    HealthStatusInfo,
    ComponentStateInfo
)

class LifecycleAware(ABC):
    """Interface for components with lifecycle management."""
    
    def __init__(self):
        """Initialize lifecycle aware component."""
        self._state_info = ComponentStateInfo(
            state=ComponentState.CREATED,
            previous_state=None,
            transition_time=datetime.now(timezone.utc)
        )
        self._health_status = HealthStatusInfo(
            status=HealthStatus.UNKNOWN,
            details={},
            state_info=self._state_info
        )
        self._is_initialized = False
        
    @property
    def state(self) -> ComponentState:
        """Get component state."""
        return self._state_info.state
    
    @state.setter
    def state(self, value: Union[str, ComponentState]) -> None:
        """Set component state with validation.
        
        Args:
            value: New state value
            
        Raises:
            ValueError: If state value is invalid or transition is not allowed
        """
        if not isinstance(self._state_info.state, ComponentState):
            self._state_info.state = ComponentState(self._state_info.state)

        if isinstance(value, str):
            try:
                value = ComponentState(value)
            except ValueError:
                raise ValueError(f"Invalid state value: {value}")
                
        if not (isinstance(value, ComponentState) or isinstance(self._state_info.state, ComponentState)):
            raise ValueError(f"Invalid state types: (prev: {(self._state_info.state, type(self._state_info.state))}, new: {(value, type(value))})")
            
        # Validate state transition
        if not self._state_info.state.validate_transition(value):
            raise ValueError(
                f"Invalid state transition from {self._state_info.state.value} to {value.value}"
            )
            
        # Update state info
        self._state_info.update(
            state=value,
            metadata={
                "previous_state": self._state_info.state.value,
                "transition_time": datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Update health status with new state info
        self._health_status.update(state_info=self._state_info)
        
    @property
    def health_status(self) -> HealthStatusInfo:
        """Get component health status."""
        return self._health_status
            
    @health_status.setter
    def health_status(self, value: HealthStatusInfo) -> None:
        """Set component health status."""
        self._health_status = value
        
    @property
    def state_info(self) -> ComponentStateInfo:
        """Get component state information."""
        return self._state_info
        
    @property
    def is_initialized(self) -> bool:
        """Get initialization status."""
        return self._is_initialized
        
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize component.
        
        This method should be called before start() and should perform
        any necessary setup or resource allocation.
        """
        pass
        
    @abstractmethod
    async def start(self) -> None:
        """Start component.
        
        This method should be called after initialize() and should start
        any background tasks or services.
        """
        pass
        
    @abstractmethod
    async def stop(self) -> None:
        """Stop component.
        
        This method should stop any background tasks and release resources.
        """
        pass
        
    @abstractmethod
    async def check_health(self) -> HealthStatusInfo:
        """Check component health.
        
        Returns:
            Current health status information
        """
        pass
        
    async def _initialize_impl(self) -> None:
        """Implementation of component initialization.
        
        This method should be overridden by subclasses to provide
        component-specific initialization logic.
        """
        pass
        
    async def _start_impl(self) -> None:
        """Implementation of component start.
        
        This method should be overridden by subclasses to provide
        component-specific start logic.
        """
        pass
        
    async def _stop_impl(self) -> None:
        """Implementation of component stop.
        
        This method should be overridden by subclasses to provide
        component-specific stop logic.
        """
        pass
        
    async def _check_health_impl(self) -> None:
        """Implementation of health check.
        
        This method should be overridden by subclasses to provide
        component-specific health check logic.
        """
        pass 