"""Core chat type definitions."""
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import Field

from core.types.model import CoreBaseModel
from core.types.websocket import MessageType, MessageDirection, MessageStatus
from core.types.session import SessionType, SessionState
from core.types.audio import AudioFormat, AudioQuality, TranscriptionMode


class ChatState(str, Enum):
    """Chat state enumeration."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"

class ChatType(str, Enum):
    """Chat type enumeration."""
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"

class ChatEventType(str, Enum):
    """Chat event types."""
    # Message events
    MESSAGE_ADDED = "message_added"
    MESSAGE_UPDATED = "message_updated"
    MESSAGE_DELETED = "message_deleted"
    
    # Session events
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"
    SESSION_PAUSED = "session_paused"
    SESSION_RESUMED = "session_resumed"
    SESSION_ARCHIVED = "session_archived"
    
    # Audio events
    AUDIO_STARTED = "audio_started"
    AUDIO_STOPPED = "audio_stopped"
    AUDIO_TRANSCRIBED = "audio_transcribed"
    AUDIO_PLAYBACK_STARTED = "audio_playback_started"
    AUDIO_PLAYBACK_STOPPED = "audio_playback_stopped"
    
    # Analysis events
    ANALYSIS_STARTED = "analysis_started"
    ANALYSIS_PROGRESS = "analysis_progress"
    ANALYSIS_COMPLETED = "analysis_completed"
    ANALYSIS_ERROR = "analysis_error"


class AudioMessageMetadata(CoreBaseModel):
    """Audio message metadata."""
    format: AudioFormat = Field(description="Audio format")
    quality: AudioQuality = Field(description="Audio quality")
    duration: float = Field(description="Audio duration in seconds")
    transcription_mode: TranscriptionMode = Field(description="Transcription mode")
    transcript: Optional[str] = Field(None, description="Transcribed text")
    audio_url: Optional[str] = Field(None, description="Audio file URL")
    is_final: bool = Field(default=False, description="Whether transcription is final")


class AnalysisMetadata(CoreBaseModel):
    """Analysis metadata."""
    analysis_type: str = Field(description="Type of analysis")
    confidence_score: float = Field(description="Analysis confidence score")
    sentiment: Optional[Dict[str, float]] = Field(None, description="Sentiment analysis")
    topics: Optional[List[str]] = Field(None, description="Identified topics")
    entities: Optional[List[Dict[str, Any]]] = Field(None, description="Named entities")
    keywords: Optional[List[str]] = Field(None, description="Key phrases")
    summary: Optional[str] = Field(None, description="Content summary")


class ChatMessage(CoreBaseModel):
    """Chat message model."""
    id: UUID = Field(description="Message ID")
    session_id: UUID = Field(description="Session ID")
    role: str = Field(description="Message role (user/assistant)")
    content: str = Field(description="Message content")
    type: MessageType = Field(default=MessageType.TEXT, description="Message type")
    direction: MessageDirection = Field(description="Message direction")
    status: MessageStatus = Field(description="Message status")
    audio_metadata: Optional[AudioMessageMetadata] = Field(None, description="Audio-specific metadata")
    analysis_metadata: Optional[AnalysisMetadata] = Field(None, description="Analysis metadata")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "role": self.role,
            "content": self.content,
            "type": self.type.value,
            "direction": self.direction.value,
            "status": self.status.value,
            "audio_metadata": self.audio_metadata.dict() if self.audio_metadata else None,
            "analysis_metadata": self.analysis_metadata.dict() if self.analysis_metadata else None,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class ChatSession(CoreBaseModel):
    """Chat session model."""
    id: UUID = Field(description="Session ID")
    user_id: UUID = Field(description="User ID")
    title: str = Field(description="Session title")
    session_type: SessionType = Field(description="Session type")
    state: SessionState = Field(default=SessionState.ACTIVE, description="Session state")
    chat_state: ChatState = Field(default=ChatState.ACTIVE, description="Chat state")
    messages: List[ChatMessage] = Field(default_factory=list, description="Session messages")
    audio_settings: Optional[Dict[str, Any]] = Field(None, description="Audio configuration")
    analysis_settings: Optional[Dict[str, Any]] = Field(None, description="Analysis configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "session_type": self.session_type.value,
            "state": self.state.value,
            "chat_state": self.chat_state.value,
            "messages": [msg.to_dict() for msg in self.messages],
            "audio_settings": self.audio_settings,
            "analysis_settings": self.analysis_settings,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class ChatEvent(CoreBaseModel):
    """Chat event model."""
    type: ChatEventType = Field(description="Event type")
    session_id: UUID = Field(description="Session ID")
    data: Dict[str, Any] = Field(description="Event data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "type": self.type.value,
            "session_id": str(self.session_id),
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        } 