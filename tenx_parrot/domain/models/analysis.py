"""Analysis domain models."""
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from uuid import UUID
from pydantic import Field, model_validator, computed_field

from core.types.model import CoreBaseModel
from core.types.analysis import (
    AnalysisResult,
    AnalysisMetric,
    AnalysisType,
    AnalysisStatus,
    QuestionStatus
)


class QuestionAnalysis(CoreBaseModel):
    """Question analysis domain model."""
    
    id: UUID = Field(description="Question analysis ID")
    question_id: str = Field(description="Question ID")
    category: str = Field(description="Question category")
    status: QuestionStatus = Field(description="Question status")
    score: Optional[float] = Field(default=None, description="Question score", ge=0.0, le=100.0)
    feedback: Optional[str] = Field(default=None, description="Question feedback")
    duration: Optional[float] = Field(default=None, description="Analysis duration in seconds")


class SessionAnalysis(CoreBaseModel):
    """Session analysis domain model."""
    
    id: UUID = Field(description="Session analysis ID")
    session_id: UUID = Field(description="Session ID")
    user_id: UUID = Field(description="User ID")
    job_id: UUID = Field(description="Job ID")
    start_time: datetime = Field(description="Session start time")
    end_time: Optional[datetime] = Field(default=None, description="Session end time")
    status: AnalysisStatus = Field(description="Analysis status")
    total_questions: int = Field(description="Total questions", ge=0)
    completed_questions: int = Field(description="Completed questions", ge=0)
    progress_percentage: float = Field(description="Progress percentage", ge=0.0, le=100.0)
    average_score: Optional[float] = Field(default=None, description="Average score", ge=0.0, le=100.0)
    questions: List[QuestionAnalysis] = Field(default_factory=list, description="Question analyses")
    feedback: Optional[Dict[str, Any]] = Field(default=None, description="Session feedback")
    
    @model_validator(mode='after')
    def validate_progress(self) -> 'SessionAnalysis':
        """Validate progress metrics."""
        if self.completed_questions > self.total_questions:
            raise ValueError("Completed questions cannot exceed total questions")
        if self.total_questions > 0:
            self.progress_percentage = (self.completed_questions / self.total_questions) * 100
        return self
    
    def add_question_analysis(self, analysis: QuestionAnalysis) -> None:
        """Add question analysis.
        
        Args:
            analysis: Question analysis to add
        """
        self.questions.append(analysis)
        self.completed_questions += 1
        
        # Update average score
        if self.questions:
            scores = [q.score for q in self.questions if q.score is not None]
            if scores:
                self.average_score = sum(scores) / len(scores)
    
    def complete(self) -> None:
        """Complete session analysis."""
        self.status = AnalysisStatus.COMPLETED
        self.end_time = datetime.now()
    
    def fail(self, error: str) -> None:
        """Mark session analysis as failed.
        
        Args:
            error: Error message
        """
        self.status = AnalysisStatus.FAILED
        if not self.feedback:
            self.feedback = {}
        self.feedback["error"] = error


class AnalysisDTO(CoreBaseModel):
    """Analysis Data Transfer Object."""
    id: UUID = Field(description="Analysis ID")
    session_id: UUID = Field(description="Session ID")
    type: AnalysisType = Field(description="Analysis type")
    status: AnalysisStatus = Field(description="Analysis status")
    confidence_score: float = Field(description="Analysis confidence score")
    sentiment: Optional[str] = Field(default=None, description="Sentiment analysis")
    topics: List[str] = Field(default_factory=list, description="Identified topics")
    entities: List[str] = Field(default_factory=list, description="Identified entities")
    keywords: List[str] = Field(default_factory=list, description="Key terms")
    summary: Optional[str] = Field(default=None, description="Analysis summary")
    metrics: List[AnalysisMetric] = Field(default_factory=list, description="Analysis metrics")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")

    @classmethod
    def from_analysis(cls, analysis: AnalysisResult) -> "AnalysisDTO":
        """Create DTO from analysis result.
        
        Args:
            analysis: Analysis result
            
        Returns:
            Analysis DTO
        """
        return cls(**analysis.dict())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "type": self.type.value,
            "status": self.status.value,
            "confidence_score": self.confidence_score,
            "sentiment": self.sentiment,
            "topics": self.topics,
            "entities": self.entities,
            "keywords": self.keywords,
            "summary": self.summary,
            "metrics": [metric.dict() for metric in self.metrics],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class AnalysisMetricsDTO(CoreBaseModel):
    """Analysis metrics DTO."""
    total_analyses: int = Field(description="Total number of analyses")
    completed_analyses: int = Field(description="Number of completed analyses")
    average_confidence: float = Field(description="Average confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metrics metadata")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Metrics timestamp")

    @computed_field
    def completion_rate(self) -> float:
        """Calculate completion rate."""
        if self.total_analyses == 0:
            return 0.0
        return (self.completed_analyses / self.total_analyses) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_analyses": self.total_analyses,
            "completed_analyses": self.completed_analyses,
            "average_confidence": self.average_confidence,
            "completion_rate": self.completion_rate,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }