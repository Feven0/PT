"""Core analysis type definitions."""
from __future__ import annotations
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from uuid import UUID
from pydantic import Field, computed_field
from enum import Enum
from core.types.model import CoreBaseModel


class AnalysisType(str, Enum):
    """Analysis type enumeration."""
    SESSION = "session"
    QUESTION = "question"
    OVERALL = "overall"
    PERFORMANCE = "performance"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    SYSTEM = "system"
    AUDIO = "audio"
    TEXT = "text"
    TRANSCRIPT = "transcript"
    SENTIMENT = "sentiment"
    TOPICS = "topics"
    ENTITIES = "entities"
    KEYWORDS = "keywords"
    SUMMARY = "summary"


class AnalysisStatus(str, Enum):
    """Analysis status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    VALIDATING = "validating"
    PROCESSING = "processing"
    STREAMING = "streaming"
    PAUSED = "paused"
    RESUMED = "resumed"
    ARCHIVED = "archived"


class QuestionStatus(str, Enum):
    """Question analysis status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMED_OUT = "timed_out"
    VALIDATING = "validating"
    PROCESSING = "processing"
    STREAMING = "streaming"
    PAUSED = "paused"
    RESUMED = "resumed"
    ARCHIVED = "archived"


class AnalysisMetric(CoreBaseModel):
    """Analysis metric model."""
    name: str = Field(description="Metric name")
    score: float = Field(description="Metric score")
    weight: float = Field(description="Metric weight")
    feedback: str = Field(description="Metric feedback")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional metric details")


class AnalysisResult(CoreBaseModel):
    """Analysis result model."""
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

    @computed_field
    def overall_score(self) -> float:
        """Calculate overall analysis score."""
        if not self.metrics:
            return 0.0
            
        total_weight = sum(metric.weight for metric in self.metrics)
        if total_weight == 0:
            return 0.0
            
        weighted_sum = sum(metric.score * metric.weight for metric in self.metrics)
        return weighted_sum / total_weight

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
            "updated_at": self.updated_at.isoformat(),
            "overall_score": self.overall_score
        }

    def update_status(self, new_status: AnalysisStatus) -> None:
        """Update analysis status.
        
        Args:
            new_status: New status
        """
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

    def add_metadata(self, updates: Dict[str, Any]) -> None:
        """Add metadata updates.
        
        Args:
            updates: Metadata updates
        """
        self.metadata.update(updates)
        self.updated_at = datetime.now(timezone.utc)

    def add_metric(self, metric: AnalysisMetric) -> None:
        """Add analysis metric."""
        self.metrics.append(metric)
        self.updated_at = datetime.now(timezone.utc) 