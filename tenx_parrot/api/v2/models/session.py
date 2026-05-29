"""Session API models."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from core.types.session import SessionState, SessionType, SessionProgress
from core.types.metrics import MetricType


class CreateSessionRequest(BaseModel):
    """Request model for creating a session."""
    user_id: str = Field(..., description="User identifier")
    session_type: SessionType = Field(default=SessionType.INTERACTIVE, description="Session type")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ClarificationRequest(BaseModel):
    """Request model for question clarification."""
    question: str = Field(..., description="Question to clarify")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class SessionResponse(BaseModel):
    """Response model for session operations."""
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")
    state: SessionState = Field(..., description="Current session state")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")


class SessionProgressResponse(BaseModel):
    """Response model for session progress."""
    session_id: str = Field(..., description="Session identifier")
    progress: float = Field(..., ge=0.0, le=1.0, description="Session progress (0-1)")
    state: SessionState = Field(..., description="Current session state")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Session metrics")


class ChatHistoryResponse(BaseModel):
    """Response model for chat history."""
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Chat messages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chat history metadata")


class UserSessionsResponse(BaseModel):
    """Response model for user sessions."""
    sessions: List[SessionResponse] = Field(default_factory=list, description="User sessions")
    total: int = Field(..., description="Total number of sessions")
    has_more: bool = Field(default=False, description="Whether more sessions exist")


class AdminOverviewResponse(BaseModel):
    """Response model for admin overview."""
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    total_sessions: int = Field(..., description="Total number of sessions")
    active_sessions: int = Field(..., description="Number of active sessions")
    total_jobs: int = Field(..., description="Total number of jobs")
    active_jobs: int = Field(..., description="Number of active jobs")
    system_metrics: Dict[str, Any] = Field(default_factory=dict, description="System metrics")
    recent_activities: List[Dict[str, Any]] = Field(default_factory=list, description="Recent activities")


class UserPerformanceResponse(BaseModel):
    """Response model for user performance."""
    user_id: str = Field(..., description="User identifier")
    total_sessions: int = Field(..., description="Total number of sessions")
    completed_sessions: int = Field(..., description="Number of completed sessions")
    average_duration: float = Field(..., description="Average session duration")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    engagement_score: float = Field(..., ge=0.0, le=1.0, description="User engagement score")
    last_activity: datetime = Field(..., description="Last activity timestamp")


class JobStatisticsResponse(BaseModel):
    """Response model for job statistics."""
    job_id: str = Field(..., description="Job identifier")
    total_applications: int = Field(..., description="Total number of applications")
    completed_interviews: int = Field(..., description="Number of completed interviews")
    average_duration: float = Field(..., description="Average interview duration")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Interview success rate")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Job-specific metrics")
    last_updated: datetime = Field(..., description="Last update timestamp") 