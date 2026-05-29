"""Core session type definitions."""
from __future__ import annotations
from typing import Any, Dict, Optional, Protocol, runtime_checkable, Generic, TypeVar, List
from uuid import UUID
from datetime import datetime, timezone
from pydantic import Field, computed_field, model_validator
from enum import Enum
from core.types.model import CoreBaseModel
from core.types.websocket import ConnectionState

T = TypeVar('T', bound='CoreBaseModel')

class SessionState(str, Enum):
    """Base session state."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TIMED_OUT = "timed_out"
    CLOSED = "closed"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ARCHIVED = "archived"
    FAILED = "failed"


class SessionType(str, Enum):
    """Session type enumeration."""
    INTERACTIVE = "interactive"
    BACKGROUND = "background"
    SYSTEM = "system"
    CHAT = "chat"
    INTERVIEW = "interview"
    AUDIO_INTERVIEW = "audio_interview"
    TEXT_INTERVIEW = "text_interview"
    MOCK_INTERVIEW = "mock_interview"
    EVALUATION = "evaluation"
    INFORMATION = "information"
    STATUS = "status"


class SessionConfig(CoreBaseModel):
    """Session configuration."""
    timeout_seconds: int = Field(default=3600, description="Session timeout in seconds")
    max_inactive_seconds: int = Field(default=1800, description="Maximum inactivity period in seconds")
    auto_reconnect: bool = Field(default=True, description="Whether to allow automatic reconnection")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional configuration metadata")


class SessionStateModel(CoreBaseModel):
    """Session state model."""
    status: SessionState = Field(description="Current session state")
    websocket_state: ConnectionState = Field(description="WebSocket connection state")
    last_activity: datetime = Field(description="Last activity timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="State metadata")


class Session(CoreBaseModel):
    """Base session model."""
    id: UUID = Field(description="Session ID")
    user_id: UUID = Field(description="User ID")
    session_type: SessionType = Field(description="Type of session")
    title: str = Field(description="Session title")
    state: SessionState = Field(default=SessionState.ACTIVE, description="Current session state")
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Session start time")
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last activity timestamp")
    end_time: Optional[datetime] = Field(default=None, description="Session end time")
    duration_seconds: Optional[int] = Field(default=None, description="Total session duration in seconds")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Session messages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional session metadata")
    config: Dict[str, Any] = Field(default_factory=dict, description="Session configuration")
    data: Dict[str, Any] = Field(default_factory=dict, description="Session-specific data")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")
    
    @model_validator(mode='after')
    def validate_timestamps(self) -> 'Session':
        """Validate timestamp sequence."""
        if self.end_time and self.end_time < self.start_time:
            raise ValueError("End time cannot be before start time")
        if self.last_activity and self.last_activity < self.start_time:
            raise ValueError("Last activity cannot be before start time")
        return self
    
    @computed_field
    def age(self) -> float:
        """Get session age in seconds."""
        return (datetime.now(timezone.utc) - self.created_at).total_seconds()

    @computed_field
    def is_active(self) -> bool:
        """Check if session is active."""
        return self.state == SessionState.ACTIVE
    
    @computed_field
    def is_timed_out(self) -> bool:
        """Check if session has timed out."""
        if not self.is_active:
            return False
        
        inactive_time = (datetime.now(timezone.utc) - self.last_activity).total_seconds()
        return inactive_time > self.config.get("max_inactive_seconds", 1800)  # 30 minutes default
    
    def add_message(self, message: Dict[str, Any]) -> None:
        """Add message to session.
        
        Args:
            message: Message to add
        """
        self.messages.append(message)
        self.last_activity = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def update_state(self, new_state: SessionState) -> None:
        """Update session state.
        
        Args:
            new_state: New session state
        """
        if new_state == SessionState.COMPLETED:
            self.end_time = datetime.now(timezone.utc)
            self.duration_seconds = int((self.end_time - self.start_time).total_seconds())
        
        self.state = new_state
        self.last_activity = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """Update session metadata.
        
        Args:
            metadata: New metadata to merge
        """
        self.metadata.update(metadata)
        self.last_activity = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """Update session configuration.
        
        Args:
            config: New configuration to merge
        """
        self.config.update(config)
        self.last_activity = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """Update session-specific data.
        
        Args:
            data: New data to merge
        """
        self.data.update(data)
        self.last_activity = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)


class SessionProgress(CoreBaseModel):
    """Session progress tracking."""
    id: str = Field(description="Session identifier")
    user_id: str = Field(description="User identifier")
    session_type: SessionType = Field(description="Type of session")
    state: SessionState = Field(description="Current session state")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")
    config: Dict[str, Any] = Field(default_factory=dict, description="Session configuration")
    data: Dict[str, Any] = Field(default_factory=dict, description="Session data")

    @computed_field
    def is_active(self) -> bool:
        """Check if session is active."""
        return self.state in {
            SessionState.ACTIVE,
            SessionState.PAUSED
        }

    @computed_field
    def duration(self) -> float:
        """Get session duration in seconds."""
        if self.is_active:
            return (datetime.now(timezone.utc) - self.created_at).total_seconds()
        return (self.updated_at - self.created_at).total_seconds()


class SessionEvent(CoreBaseModel):
    """Session event model."""
    session_id: str = Field(description="Session identifier")
    event_type: str = Field(description="Event type")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Event timestamp")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional event metadata")


class WebSocketState(CoreBaseModel):
    """WebSocket connection state."""
    connected: bool = Field(default=False, description="Whether the WebSocket is connected")
    client_id: Optional[str] = Field(default=None, description="Client identifier")
    last_seen: Optional[datetime] = Field(default=None, description="Last seen timestamp")
    connection_info: Optional[Dict[str, Any]] = Field(default=None, description="Additional connection information")


class SessionMetrics(CoreBaseModel):
    """Session metrics model."""
    total_duration: float = Field(default=0.0, description="Total session duration in seconds")
    message_count: int = Field(default=0, description="Number of messages processed")
    error_count: int = Field(default=0, description="Number of errors encountered")
    observer_count: int = Field(default=0, description="Number of session observers")
    last_activity: Optional[datetime] = Field(default=None, description="Last activity timestamp")
    custom_metrics: Dict[str, Any] = Field(default_factory=dict, description="Custom metric data")


@runtime_checkable
class SessionManagerProtocol(Protocol, Generic[T]):
    """Session manager protocol."""
    
    name: str
    state: str
    dependencies: List[str]
    
    async def create_session(
        self,
        data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """Create a new session."""
        ...
    
    async def get_session(self, session_id: UUID) -> Optional[T]:
        """Get session by ID."""
        ...
    
    async def update_session_state(
        self,
        session_id: UUID,
        updates: Dict[str, Any]
    ) -> bool:
        """Update session state."""
        ...
    
    async def delete_session(self, session_id: UUID) -> bool:
        """Delete a session."""
        ...
    
    async def list_sessions(
        self,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """List active sessions."""
        ...
    
    async def handle_interruption(
        self,
        session_id: UUID,
        reason: str
    ) -> None:
        """Handle session interruption."""
        ...
    
    async def cleanup_sessions(self) -> None:
        """Clean up expired and inactive sessions."""
        ...
    
    async def save_session_state(self, session_id: UUID) -> None:
        """Save session state to storage."""
        ...
    
    async def restore_session_state(self, session_id: UUID) -> Optional[T]:
        """Restore session state from storage."""
        ...
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        ...
    
    async def validate_session(self, session_id: UUID) -> bool:
        """Validate session state."""
        ... 