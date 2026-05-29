"""Analysis API models."""
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

from core.types.model import CoreBaseModel
from core.types.analysis import AnalysisType, AnalysisStatus, QuestionStatus


class AnalysisRequest(CoreBaseModel):
    """Request model for analysis operations."""
    start_time: Optional[datetime] = Field(default=None, description="Analysis start time")
    end_time: Optional[datetime] = Field(default=None, description="Analysis end time")
    analysis_type: str = Field(default="conversation", description="Type of analysis to perform")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AnalysisMetricResponse(CoreBaseModel):
    """Response model for analysis metrics."""
    name: str = Field(description="Metric name")
    score: float = Field(description="Metric score", ge=0.0, le=100.0)
    weight: float = Field(description="Metric weight", ge=0.0, le=1.0)
    feedback: str = Field(description="Metric feedback")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")


class QuestionAnalysisResponse(CoreBaseModel):
    """Response model for question analysis."""
    id: str = Field(description="Question analysis ID")
    question_id: str = Field(description="Question ID")
    category: str = Field(description="Question category")
    status: QuestionStatus = Field(description="Question status")
    score: Optional[float] = Field(default=None, description="Question score", ge=0.0, le=100.0)
    feedback: Optional[str] = Field(default=None, description="Question feedback")
    duration: Optional[float] = Field(default=None, description="Analysis duration in seconds")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class SessionAnalysisResponse(CoreBaseModel):
    """Response model for session analysis."""
    id: str = Field(description="Session analysis ID")
    session_id: str = Field(description="Session ID")
    user_id: str = Field(description="User ID")
    job_id: str = Field(description="Job ID")
    start_time: datetime = Field(description="Session start time")
    end_time: Optional[datetime] = Field(default=None, description="Session end time")
    status: AnalysisStatus = Field(description="Analysis status")
    total_questions: int = Field(description="Total questions", ge=0)
    completed_questions: int = Field(description="Completed questions", ge=0)
    progress_percentage: float = Field(description="Progress percentage", ge=0.0, le=100.0)
    average_score: Optional[float] = Field(default=None, description="Average score", ge=0.0, le=100.0)
    questions: List[QuestionAnalysisResponse] = Field(default_factory=list, description="Question analyses")
    feedback: Optional[Dict[str, Any]] = Field(default=None, description="Session feedback")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class AnalysisResultResponse(CoreBaseModel):
    """Response model for analysis results."""
    id: str = Field(description="Result ID")
    session_id: str = Field(description="Associated session ID")
    type: AnalysisType = Field(description="Analysis type")
    status: AnalysisStatus = Field(description="Analysis status")
    start_time: datetime = Field(description="Analysis start time")
    end_time: Optional[datetime] = Field(default=None, description="Analysis end time")
    duration: Optional[float] = Field(default=None, description="Analysis duration in seconds")
    overall_score: Optional[float] = Field(default=None, description="Overall analysis score", ge=0.0, le=100.0)
    metrics: List[AnalysisMetricResponse] = Field(default_factory=list, description="Analysis metrics")
    summary: Optional[str] = Field(default=None, description="Analysis summary")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class AnalysisResponse(CoreBaseModel):
    """Response model for analysis operations."""
    id: str = Field(description="Analysis ID")
    session_id: str = Field(description="Session ID")
    type: AnalysisType = Field(description="Analysis type")
    status: AnalysisStatus = Field(description="Analysis status")
    start_time: datetime = Field(description="Start time")
    end_time: Optional[datetime] = Field(default=None, description="End time")
    duration: Optional[float] = Field(default=None, description="Duration in seconds")
    overall_score: Optional[float] = Field(default=None, description="Overall score", ge=0.0, le=100.0)
    metrics: List[AnalysisMetricResponse] = Field(default_factory=list, description="Analysis metrics")
    summary: Optional[str] = Field(default=None, description="Analysis summary")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class RealtimeAnalysisResponse(CoreBaseModel):
    """Response model for real-time analysis."""
    session_id: str = Field(description="Session ID")
    timestamp: datetime = Field(description="Analysis timestamp")
    metrics: List[AnalysisMetricResponse] = Field(default_factory=list, description="Current metrics")
    progress: float = Field(description="Analysis progress", ge=0.0, le=100.0)
    status: AnalysisStatus = Field(description="Current status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SentimentAnalysisResponse(CoreBaseModel):
    """Response model for sentiment analysis."""
    session_id: str = Field(description="Session ID")
    timestamp: datetime = Field(description="Analysis timestamp")
    overall_sentiment: float = Field(description="Overall sentiment score", ge=-1.0, le=1.0)
    sentiment_by_topic: Dict[str, float] = Field(default_factory=dict, description="Sentiment by topic")
    sentiment_trend: List[Dict[str, Any]] = Field(default_factory=list, description="Sentiment trend over time")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TopicAnalysisResponse(CoreBaseModel):
    """Response model for topic analysis."""
    session_id: str = Field(description="Session ID")
    timestamp: datetime = Field(description="Analysis timestamp")
    topics: List[Dict[str, Any]] = Field(default_factory=list, description="Identified topics")
    topic_confidence: Dict[str, float] = Field(default_factory=dict, description="Topic confidence scores")
    topic_duration: Dict[str, float] = Field(default_factory=dict, description="Topic duration in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class EngagementAnalysisResponse(CoreBaseModel):
    """Response model for engagement analysis."""
    session_id: str = Field(description="Session ID")
    timestamp: datetime = Field(description="Analysis timestamp")
    engagement_score: float = Field(description="Overall engagement score", ge=0.0, le=100.0)
    engagement_by_topic: Dict[str, float] = Field(default_factory=dict, description="Engagement by topic")
    engagement_trend: List[Dict[str, Any]] = Field(default_factory=list, description="Engagement trend over time")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PerformanceAnalysisResponse(CoreBaseModel):
    """Response model for performance analysis."""
    session_id: str = Field(description="Session ID")
    timestamp: datetime = Field(description="Analysis timestamp")
    performance_score: float = Field(description="Overall performance score", ge=0.0, le=100.0)
    performance_by_category: Dict[str, float] = Field(default_factory=dict, description="Performance by category")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    improvements: List[str] = Field(default_factory=list, description="Areas for improvement")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SessionSummaryResponse(CoreBaseModel):
    """Response model for session summary."""
    session_id: str = Field(description="Session ID")
    timestamp: datetime = Field(description="Analysis timestamp")
    summary: str = Field(description="Session summary")
    key_points: List[str] = Field(default_factory=list, description="Key points")
    duration: float = Field(description="Session duration in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class RecommendationsResponse(CoreBaseModel):
    """Response model for recommendations."""
    session_id: str = Field(description="Session ID")
    timestamp: datetime = Field(description="Analysis timestamp")
    recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="Recommendations")
    priority: Dict[str, str] = Field(default_factory=dict, description="Recommendation priorities")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata") 