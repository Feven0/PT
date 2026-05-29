"""Core WebSocket type definitions."""
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum
from pydantic import Field
from core.types.model import CoreBaseModel

class ConnectionState(str, Enum):
    """WebSocket connection states."""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"

class EventType(str, Enum):
    """WebSocket event types."""
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    MESSAGE = "message"
    STATE_CHANGE = "state_change"
    ERROR = "error"
    HEARTBEAT = "heartbeat"

class MessageType(str, Enum):
    """Message types."""
    TEXT = "text"
    AUDIO = "audio"
    STATE = "state"
    NOTIFICATION = "notification"
    ERROR = "error"

class MessageDirection(str, Enum):
    """Message direction."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"

class MessageStatus(str, Enum):
    """Message status."""
    PENDING = "pending"
    DELIVERED = "delivered"
    READ = "read"
    ERROR = "error"

class SocketEvent(str, Enum):
    """SocketIO event types."""
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    ERROR = "error"
    MESSAGE = "message"
    STATE_CHANGE = "state_change"
    NOTIFICATION = "notification"
    SESSION_STATE = "session.state"
    SESSION_MESSAGE = "session.message"
    
    # Chat events
    CHAT_MESSAGE = "chat.message"
    CHAT_TYPING = "chat.typing"
    CHAT_HISTORY = "chat.history"
    
    # Interview events
    INTERVIEW_START = "interview.start"
    INTERVIEW_QUESTION = "interview.question"
    INTERVIEW_ANSWER = "interview.answer"
    INTERVIEW_FEEDBACK = "interview.feedback"
    INTERVIEW_COMPLETE = "interview.complete"
    
    # Analysis events
    ANALYSIS_START = "analysis.start"
    ANALYSIS_PROGRESS = "analysis.progress"
    ANALYSIS_COMPLETE = "analysis.complete"
    
    # WebRTC events
    WEBRTC_OFFER = "webrtc.offer"
    WEBRTC_ANSWER = "webrtc.answer"
    WEBRTC_ICE = "webrtc.ice-candidate"

class SocketEventData(CoreBaseModel):
    """SocketIO event data."""
    event: SocketEvent
    data: Dict[str, Any]
    room: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

class StateChangeEvent(CoreBaseModel):
    """State change event data."""
    session_id: str = Field(description="Session identifier")
    previous_state: Dict[str, Any] = Field(description="Previous state data")
    new_state: Dict[str, Any] = Field(description="New state data")
    change_reason: Optional[str] = Field(default=None, description="Reason for state change")
    timestamp: datetime = Field(default_factory=datetime.now, description="Event timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional event metadata")

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary format."""
        return {
            "session_id": self.session_id,
            "previous_state": self.previous_state,
            "new_state": self.new_state,
            "change_reason": self.change_reason,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

class TextMessage(CoreBaseModel):
    """Text message model."""
    type: MessageType = MessageType.TEXT
    content: str
    direction: MessageDirection
    status: MessageStatus
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

class AudioMessage(CoreBaseModel):
    """Audio message model."""
    type: MessageType = MessageType.AUDIO
    content_url: str
    duration: float
    transcript: Optional[str] = None
    direction: MessageDirection
    status: MessageStatus
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

class StateMessage(CoreBaseModel):
    """State message model."""
    type: MessageType = MessageType.STATE
    state_type: str
    state_data: Dict[str, Any]
    is_partial: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

class NotificationMessage(CoreBaseModel):
    """Notification message model."""
    type: MessageType = MessageType.NOTIFICATION
    title: str
    body: str
    level: str = "info"
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

class ErrorMessage(CoreBaseModel):
    """Error message model."""
    type: MessageType = MessageType.ERROR
    error: str
    code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

# Union of all possible message types
Message = Union[
    TextMessage,
    AudioMessage,
    StateMessage,
    NotificationMessage,
    ErrorMessage,
    StateChangeEvent,
    SocketEventData
]