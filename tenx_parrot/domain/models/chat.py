"""Domain models for chat."""
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID
from pydantic import Field, ConfigDict

from core.types.model import CoreBaseModel
from core.types.chat import (
    ChatState,
    ChatEventType,
    ChatMessage,
    ChatSession,
    ChatEvent,
    AudioMessageMetadata,
    AnalysisMetadata
)


class ChatMessageDTO(CoreBaseModel):
    """Chat message DTO for API responses."""
    id: UUID = Field(description="Message ID")
    session_id: UUID = Field(description="Session ID")
    role: str = Field(description="Message role (user/assistant)")
    content: str = Field(description="Message content")
    type: str = Field(description="Message type")
    direction: str = Field(description="Message direction")
    status: str = Field(description="Message status")
    audio_metadata: Optional[Dict[str, Any]] = Field(None, description="Audio-specific metadata")
    analysis_metadata: Optional[Dict[str, Any]] = Field(None, description="Analysis metadata")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    @classmethod
    def from_chat_message(cls, message: ChatMessage) -> "ChatMessageDTO":
        """Create DTO from ChatMessage."""
        return cls(
            id=message.id,
            session_id=message.session_id,
            role=message.role,
            content=message.content,
            type=message.type.value,
            direction=message.direction.value,
            status=message.status.value,
            audio_metadata=message.audio_metadata.dict() if message.audio_metadata else None,
            analysis_metadata=message.analysis_metadata.dict() if message.analysis_metadata else None,
            metadata=message.metadata,
            created_at=message.created_at,
            updated_at=message.updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary."""
        return {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "role": self.role,
            "content": self.content,
            "type": self.type,
            "direction": self.direction,
            "status": self.status,
            "audio_metadata": self.audio_metadata,
            "analysis_metadata": self.analysis_metadata,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class ChatSessionDTO(CoreBaseModel):
    """Chat session DTO for API responses."""
    id: UUID = Field(description="Session ID")
    user_id: UUID = Field(description="User ID")
    title: str = Field(description="Session title")
    session_type: str = Field(description="Session type")
    state: str = Field(description="Session state")
    chat_state: str = Field(description="Chat state")
    message_count: int = Field(description="Number of messages")
    audio_settings: Optional[Dict[str, Any]] = Field(None, description="Audio configuration")
    analysis_settings: Optional[Dict[str, Any]] = Field(None, description="Analysis configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")
    messages: List[ChatMessageDTO] = Field(default_factory=list, description="Session messages")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    @classmethod
    def from_chat_session(cls, session: ChatSession) -> "ChatSessionDTO":
        """Create DTO from ChatSession."""
        return cls(
            id=session.id,
            user_id=session.user_id,
            title=session.title,
            session_type=session.session_type.value,
            state=session.state.value,
            chat_state=session.chat_state.value,
            message_count=len(session.messages),
            audio_settings=session.audio_settings,
            analysis_settings=session.analysis_settings,
            metadata=session.metadata,
            messages=[ChatMessageDTO.from_chat_message(msg) for msg in session.messages],
            created_at=session.created_at,
            updated_at=session.updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "session_type": self.session_type,
            "state": self.state,
            "chat_state": self.chat_state,
            "message_count": self.message_count,
            "audio_settings": self.audio_settings,
            "analysis_settings": self.analysis_settings,
            "metadata": self.metadata,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class ChatEventDTO(CoreBaseModel):
    """Chat event DTO for API responses."""
    type: str = Field(description="Event type")
    session_id: UUID = Field(description="Session ID")
    data: Dict[str, Any] = Field(description="Event data")
    timestamp: datetime = Field(description="Event timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @classmethod
    def from_chat_event(cls, event: ChatEvent) -> "ChatEventDTO":
        """Create DTO from ChatEvent."""
        return cls(
            type=event.type.value,
            session_id=event.session_id,
            data=event.data,
            timestamp=event.timestamp,
            metadata=event.metadata
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary."""
        return {
            "type": self.type,
            "session_id": str(self.session_id),
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        } 