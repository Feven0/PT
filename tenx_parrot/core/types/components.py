"""Component-related type definitions."""
from enum import Enum
from typing import TypeVar, Dict, Any, Optional, Union, Set
from datetime import datetime, timezone
from pydantic import Field

from core.types.model import CoreBaseModel
from core.logging import BackendLogger

logger = BackendLogger(__name__)

# Type variable for component IDs
ID = TypeVar('ID')

# Component Names
class ComponentNames:
    """Component name constants."""
    # Core Managers
    socketio_manager = 'socketio_manager'
    metrics_manager = 'metrics_manager'
    cache_manager = 'cache_manager'
    retry_manager = 'retry_manager'
    rate_limiter = 'rate_limiter'
    circuit_breaker = 'circuit_breaker'
    alert_manager = 'alert_manager' 
    audio_manager = 'audio_manager'
    llm_manager = 'llm_manager'    
    chat_manager = 'chat_manager'
    interview_manager = 'interview_manager'
    chain_manager = 'chain_manager'
    prompt_manager = 'prompt_manager'
    logger = 'logger'

    #alias
    metrics = metrics_manager
    rate_limiter_manager = rate_limiter
    circuit_breaker_manager = circuit_breaker
    
    # Infrastructure Clients
    s3_client = 's3_client'
    gdrive_client = 'gdrive_client'
    storage_client = 'storage_client'
    strapi_client = 'strapi_client'
    weaviate_client = 'weaviate_client'
    storage_infrastructure_client = 'storage_infrastructure_client'
    
    # Session Managers
    core_session_manager = 'core_session_manager'
    interview_session_manager = 'interview_session_manager'
    session_manager = 'session_manager'

    # WebSocket Managers
    websocket_manager = 'websocket_manager'
    websocket_service = 'websocket_service'
    webrtc_service = 'webrtc_service'

    # Repositories
    user_repository = 'user_repository'
    interview_repository = 'interview_repository'
    session_repository = 'session_repository'
    admin_repository = 'admin_repository'
    observer_repository = 'observer_repository'
    overall_observer_repository = 'overall_observer_repository'
    storage_repository = 'storage_repository'
    analysis_repository = 'analysis_repository'
    llm_metrics_repository = 'llm_metrics_repository'
    prompt_repository = 'prompt_repository'
    
    # Services
    llm_service = 'llm_service'
    chat_llm_service = 'chat_llm_service'
    interview_llm_service = 'interview_llm_service'
    observer_service = 'observer_service'
    overall_observer_service = 'overall_observer_service'
    assembly_ai_service = 'assembly_ai_service'
    session_service = 'session_service'
    interview_service = 'interview_service'
    interview_session_service = 'interview_session_service'
    chat_service = 'chat_service'
    
    storage_service = 'storage_service'
    analysis_service = 'analysis_service'
    admin_service = 'admin_service'
    llm_metrics_service = 'llm_metrics_service'
    
    # Middleware
    error_handler = 'error_handler'
    request_processor = 'request_processor'
    health_check = 'health_check'

    
class ComponentState(str, Enum):
    """Component lifecycle states."""
    CREATED = "created"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    DISABLED = "disabled"

    @property
    def is_active(self) -> bool:
        """Check if component is in an active state."""
        return self in {
            ComponentState.RUNNING,
            ComponentState.STARTING,
            ComponentState.INITIALIZING
        }
    
    @property
    def is_inactive(self) -> bool:
        """Check if component is in an inactive state."""
        return self in {
            ComponentState.STOPPED,
            ComponentState.FAILED
        }
    
    @property
    def can_initialize(self) -> bool:
        """Check if component can be initialized."""
        return self in {
            ComponentState.CREATED,
            ComponentState.STOPPED,
            ComponentState.FAILED
        }
    
    @property
    def can_start(self) -> bool:
        """Check if component can be started."""
        return self in {
            ComponentState.INITIALIZED,
            ComponentState.STOPPED
        }
    
    @property
    def can_stop(self) -> bool:
        """Check if component can be stopped."""
        return self in {
            ComponentState.RUNNING,
            ComponentState.STARTING,
            ComponentState.INITIALIZED
        }

    def validate_transition(self, next_state: 'ComponentState') -> bool:
        """Validate if transition to next state is allowed.
        
        Args:
            next_state: Target state to transition to
            
        Returns:
            True if transition is valid, False otherwise
        """

        valid_transitions = {
            ComponentState.CREATED: {
                ComponentState.INITIALIZING,
                ComponentState.FAILED
            },
            ComponentState.INITIALIZING: {
                ComponentState.INITIALIZED,
                ComponentState.FAILED
            },
            ComponentState.INITIALIZED: {
                ComponentState.STARTING,
                ComponentState.FAILED,
                ComponentState.STOPPING
            },
            ComponentState.STARTING: {
                ComponentState.RUNNING,
                ComponentState.FAILED,
                ComponentState.STOPPING
            },
            ComponentState.RUNNING: {
                ComponentState.STOPPING,
                ComponentState.FAILED
            },
            ComponentState.STOPPING: {
                ComponentState.STOPPED,
                ComponentState.FAILED
            },
            ComponentState.STOPPED: {
                ComponentState.INITIALIZING,
                ComponentState.FAILED
            },
            ComponentState.FAILED: {
                ComponentState.INITIALIZING,
                ComponentState.STOPPED
            },
            ComponentState.DISABLED: {
                next_state
            }            
        }
        is_valid = next_state in valid_transitions.get(self, set())
        if not is_valid and not next_state==self:
            logger.warning(
                "invalid_component_state_transition",
                from_state=self,
                to_state=next_state
            )
        return True

class HealthStatus(str, Enum):
    """Component health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    STARTING = "starting"
    STOPPING = "stopping"
    STOPPED = "stopped"
    SHUTTING_DOWN = "shutting_down"

    @property
    def is_healthy(self) -> bool:
        """Check if the health status is healthy."""
        return self == HealthStatus.HEALTHY
    
    @property
    def needs_attention(self) -> bool:
        """Check if the health status needs attention."""
        return self in [HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]

class ComponentStateInfo(CoreBaseModel):
    """Component state information container."""
    
    state: ComponentState = Field(default=ComponentState.CREATED, description="Current state")
    previous_state: Optional[ComponentState] = Field(default=None, description="Previous state")
    transition_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last transition time")
    error: Optional[str] = Field(default=None, description="Error message if in failed state")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional state metadata")

    def update(
        self,
        state: ComponentState,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update component state.
        
        Args:
            state: New state
            error: Optional error message
            metadata: Optional metadata
            
        Returns:
            True if state was updated, False if invalid transition
        """
        if not self.state.validate_transition(state):
            return False
            
        self.previous_state = self.state
        self.state = state
        self.transition_time = datetime.now(timezone.utc)
        self.error = error
        if metadata:
            self.metadata.update(metadata)
        return True

class HealthStatusInfo(CoreBaseModel):
    """Health status information container."""
    
    status: HealthStatus = Field(default=HealthStatus.UNKNOWN, description="Health status")
    details: Dict[str, Any] = Field(default_factory=dict, description="Status details")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Status timestamp")
    state_info: Optional[ComponentStateInfo] = Field(default=None, description="Component state information")
    
    @property
    def is_healthy(self) -> bool:
        """Check if status is healthy."""
        return self.status.is_healthy
    
    @property
    def needs_attention(self) -> bool:
        """Check if status needs attention."""
        return self.status.needs_attention
    
    def update(
        self,
        status: Optional[HealthStatus] = None,
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        state_info: Optional[ComponentStateInfo] = None
    ) -> None:
        """Update health status information.
        
        Args:
            status: New status
            details: New details
            timestamp: New timestamp
            state_info: New state information
        """
        if status is not None:
            self.status = status
        if details is not None:
            self.details = details
        if timestamp is not None:
            self.timestamp = timestamp
        else:
            self.timestamp = datetime.now(timezone.utc)
        if state_info is not None:
            self.state_info = state_info