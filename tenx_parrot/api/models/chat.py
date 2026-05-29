"""Chat API models."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import Field

from core.types.model import CoreBaseModel
from core.types.chat import ChatMessage, ChatSession, ChatState


class MessageCreateDTO(CoreBaseModel):
    """Message creation request DTO."""
    content: str = Field(description="Message content")
    role: str = Field(description="Message role (user/assistant)")
    metadata: Optional[Dict] = Field(default=None, description="Additional metadata")


class MessageResponseDTO(CoreBaseModel):
    """Message response DTO."""
    id: UUID = Field(description="Message ID")
    role: str = Field(description="Message role")
    content: str = Field(description="Message content")
    type: str = Field(description="Message type")
    direction: str = Field(description="Message direction")
    status: str = Field(description="Message status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Message metadata")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    @classmethod
    def from_chat_message(cls, message: ChatMessage) -> "MessageResponseDTO":
        """Create DTO from ChatMessage."""
        return cls(
            id=message.id,
            role=message.role,
            content=message.content,
            type=message.type.value,
            direction=message.direction.value,
            status=message.status.value,
            metadata=message.metadata,
            created_at=message.created_at,
            updated_at=message.updated_at
        )


class ChatSessionCreateDTO(CoreBaseModel):
    """Chat session creation request DTO."""
    title: Optional[str] = Field(None, description="Session title")
    metadata: Optional[Dict] = Field(None, description="Additional metadata")


class ChatSessionUpdateDTO(CoreBaseModel):
    """Chat session update request DTO."""
    title: Optional[str] = Field(None, description="Session title")
    state: Optional[str] = Field(None, description="Session state")
    chat_state: Optional[str] = Field(None, description="Chat state")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ChatSessionResponseDTO(CoreBaseModel):
    """Chat session response DTO."""
    id: UUID = Field(description="Session ID")
    user_id: UUID = Field(description="User ID")
    title: str = Field(description="Session title")
    session_type: str = Field(description="Session type")
    state: str = Field(description="Session state")
    chat_state: str = Field(description="Chat state")
    message_count: int = Field(description="Number of messages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")
    messages: List[MessageResponseDTO] = Field(default_factory=list, description="Session messages")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    @classmethod
    def from_chat_session(cls, session: ChatSession) -> "ChatSessionResponseDTO":
        """Create DTO from ChatSession."""
        return cls(
            id=session.id,
            user_id=session.user_id,
            title=session.title,
            session_type=session.session_type.value,
            state=session.state.value,
            chat_state=session.chat_state.value,
            message_count=len(session.messages),
            metadata=session.metadata,
            messages=[MessageResponseDTO.from_chat_message(msg) for msg in session.messages],
            created_at=session.created_at,
            updated_at=session.updated_at
        )


class ChatHistoryRequestDTO(CoreBaseModel):
    """Chat history request DTO."""
    session_id: UUID = Field(description="Chat session ID")
    limit: Optional[int] = Field(default=50, description="Maximum number of messages")
    before: Optional[datetime] = Field(None, description="Get messages before timestamp")


class ChatHistoryResponseDTO(CoreBaseModel):
    """Chat history response DTO."""
    session_id: UUID = Field(description="Chat session ID")
    messages: List[MessageResponseDTO] = Field(description="Chat messages")
    has_more: bool = Field(description="Whether more messages exist")
    total_count: int = Field(description="Total message count") 