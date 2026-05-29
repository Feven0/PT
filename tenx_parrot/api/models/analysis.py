"""Analysis API models."""
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID
from pydantic import Field, model_validator

from core.types.model import CoreBaseModel
from core.types.analysis import (
    AnalysisMetric,
    AnalysisResult,
    AnalysisType,
    AnalysisStatus,
    QuestionStatus
)
from domain.models.analysis import (
    QuestionAnalysis,
    SessionAnalysis
)


class AnalysisMetricResponse(CoreBaseModel):
    """Analysis metric API response model."""
    
    name: str = Field(description="Metric name")
    score: float = Field(description="Metric score")
    weight: float = Field(description="Metric weight")
    feedback: str = Field(description="Metric feedback")
    details: Dict[str, Any] = Field(description="Additional details")


class QuestionAnalysisResponse(CoreBaseModel):
    """Question analysis API response model."""
    
    id: UUID = Field(description="Question analysis ID")
    question_id: str = Field(description="Question ID")
    category: str = Field(description="Question category")
    status: QuestionStatus = Field(description="Question status")
    score: Optional[float] = Field(description="Question score")
    feedback: Optional[str] = Field(description="Question feedback")
    duration: Optional[float] = Field(description="Analysis duration in seconds")


class SessionAnalysisResponse(CoreBaseModel):
    """Session analysis API response model."""
    
    id: UUID = Field(description="Session analysis ID")
    session_id: UUID = Field(description="Session ID")
    user_id: UUID = Field(description="User ID")
    job_id: UUID = Field(description="Job ID")
    start_time: datetime = Field(description="Session start time")
    end_time: Optional[datetime] = Field(description="Session end time")
    status: AnalysisStatus = Field(description="Analysis status")
    total_questions: int = Field(description="Total questions")
    completed_questions: int = Field(description="Completed questions")
    progress_percentage: float = Field(description="Progress percentage")
    average_score: Optional[float] = Field(description="Average score")
    questions: List[QuestionAnalysisResponse] = Field(description="Question analyses")
    feedback: Optional[Dict[str, Any]] = Field(description="Session feedback")


class AnalysisResultResponse(CoreBaseModel):
    """Analysis result API response model."""
    
    id: UUID = Field(description="Result ID")
    session_id: UUID = Field(description="Associated session ID")
    type: AnalysisType = Field(description="Analysis type")
    status: AnalysisStatus = Field(description="Analysis status")
    start_time: datetime = Field(description="Analysis start time")
    end_time: Optional[datetime] = Field(description="Analysis end time")
    duration: Optional[float] = Field(description="Analysis duration in seconds")
    overall_score: Optional[float] = Field(description="Overall analysis score")
    metrics: List[AnalysisMetricResponse] = Field(description="Analysis metrics")
    summary: Optional[str] = Field(description="Analysis summary")
    recommendations: List[str] = Field(description="Recommendations")
    metadata: Dict[str, Any] = Field(description="Additional metadata")


class AnalysisRequest(CoreBaseModel):
    """Analysis request model."""
    
    type: AnalysisType = Field(description="Analysis type")
    session_id: UUID = Field(description="Session ID to analyze")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class AnalysisUpdateRequest(CoreBaseModel):
    """Analysis update request model."""
    
    status: Optional[AnalysisStatus] = Field(description="New analysis status")
    summary: Optional[str] = Field(description="New analysis summary")
    recommendations: Optional[List[str]] = Field(description="New recommendations")
    metadata: Optional[Dict[str, Any]] = Field(description="Updated metadata")


class AnalysisFilter(CoreBaseModel):
    """Analysis filter model."""
    
    session_id: Optional[UUID] = Field(description="Filter by session ID")
    user_id: Optional[UUID] = Field(description="Filter by user ID")
    job_id: Optional[UUID] = Field(description="Filter by job ID")
    type: Optional[AnalysisType] = Field(description="Filter by analysis type")
    status: Optional[AnalysisStatus] = Field(description="Filter by analysis status")
    start_time: Optional[datetime] = Field(description="Filter by start time")
    end_time: Optional[datetime] = Field(description="Filter by end time")
    
    @model_validator(mode='after')
    def validate_timestamps(self) -> 'AnalysisFilter':
        """Validate timestamp sequence."""
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")
        return self 