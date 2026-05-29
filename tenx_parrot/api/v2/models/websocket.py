"""WebSocket API models."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from core.types.websocket import (
    MessageType,
    EventType,
    Message,
    TextMessage,
    AudioMessage,
    StateMessage,
    NotificationMessage,
    ErrorMessage
)


class WebSocketMessageRequest(BaseModel):
    """WebSocket message request model."""
    message: Message = Field(..., description="Message to send")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class WebSocketEventResponse(BaseModel):
    """WebSocket event response model."""
    type: EventType = Field(..., description="Event type")
    session_id: str = Field(..., description="Session identifier")
    timestamp: datetime = Field(..., description="Event timestamp")
    payload: Optional[Dict[str, Any]] = Field(default=None, description="Event payload")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Event metadata")


class AudioTranscriptionRequest(BaseModel):
    """Request model for audio transcription."""
    session_id: str = Field(..., description="Interview session identifier")
    audioblob: bytes = Field(..., description="Audio data to transcribe")
    format: str = Field("wav", description="Audio format")


class AudioTranscriptionResponse(BaseModel):
    """Response model for audio transcription."""
    query: str = Field(..., description="Transcribed text")
    confidence: float = Field(..., description="Transcription confidence score")


class AudioChatRequest(BaseModel):
    """Request model for audio chat messages."""
    session_id: str = Field(..., description="Interview session identifier")
    response: Optional[bytes] = Field(None, description="Audio response data")
    time_taken: Optional[int] = Field(None, description="Time taken to respond in seconds")
    job_profile_id: str = Field(..., description="Job profile identifier")
    all_user_id: str = Field(..., description="User identifier")
    format: str = Field("wav", description="Audio format")


class AudioChatResponse(BaseModel):
    """Response model for audio chat messages."""
    content: Dict[str, Any] = Field(..., description="Response content")
    status: Optional[str] = Field(None, description="Interview status")
    realtime_evaluation: Optional[Dict[str, Any]] = Field(None, description="Real-time evaluation metrics")
    audio_chunks: Optional[List[bytes]] = Field(None, description="Audio response chunks")


class InterviewChatRequest(BaseModel):
    """Request model for interview chat messages."""
    session_id: str = Field(..., description="Interview session identifier")
    response: Optional[str] = Field(None, description="Candidate's response")
    time_taken: Optional[int] = Field(None, description="Time taken to respond in seconds")
    job_profile_id: str = Field(..., description="Job profile identifier")
    all_user_id: str = Field(..., description="User identifier")


class InterviewChatResponse(BaseModel):
    """Response model for interview chat messages."""
    content: Dict[str, Any] = Field(..., description="Response content")
    status: Optional[str] = Field(None, description="Interview status")
    realtime_evaluation: Optional[Dict[str, Any]] = Field(None, description="Real-time evaluation metrics")


class SessionData(BaseModel):
    """Model for session data."""
    id: str = Field(..., description="Session identifier")
    attributes: Dict[str, Any] = Field(..., description="Session attributes")
    status: str = Field(..., description="Session status")
    created_at: datetime = Field(..., description="Session creation timestamp") 