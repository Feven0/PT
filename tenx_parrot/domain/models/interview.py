"""Domain models for interviews."""
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from uuid import UUID
from pydantic import Field, ConfigDict

from core.types.model import CoreBaseModel
from core.types.interview import (
    InterviewState,
    InterviewType,
    InterviewMode,
    InterviewRole,
    InterviewScore,
    InterviewFeedback,
    InterviewQuestion,
    InterviewResponse,
    InterviewStep,
    InterviewFlow
)


class InterviewConfig(CoreBaseModel):
    """Interview configuration."""
    mode: InterviewMode = Field(description="Interview mode")
    role: InterviewRole = Field(description="LLM role in interview")
    type: InterviewType = Field(description="Interview type")
    max_duration: int = Field(description="Maximum duration in seconds", gt=0)
    max_questions: int = Field(description="Maximum number of questions", gt=0)
    min_response_words: int = Field(description="Minimum words in response", gt=0)
    evaluation_metrics: List[str] = Field(description="Evaluation metrics")
    question_prompt: str = Field(description="Question generation prompt template")
    answer_prompt: str = Field(description="Answer analysis prompt template")
    feedback_prompt: str = Field(description="Feedback generation prompt template")
    rubric_id: Optional[str] = Field(default=None, description="External rubric ID")
    rubric_config: Optional[Dict[str, Any]] = Field(default=None, description="Rubric configuration")
    streaming_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": True,
            "chunk_size": 1000,
            "delay": 0.1,
            "include_metadata": True
        },
        description="Streaming configuration"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional configuration")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra='allow'
    )


class Interview(CoreBaseModel):
    """Interview domain model."""
    id: UUID = Field(description="Interview ID")
    user_id: UUID = Field(description="User ID")
    flow_id: str = Field(description="Interview flow ID")
    title: str = Field(description="Interview title")
    description: str = Field(description="Interview description")
    state: InterviewState = Field(default=InterviewState.PENDING, description="Interview state")
    flow: InterviewFlow = Field(description="Interview flow configuration")
    questions: List[InterviewQuestion] = Field(default_factory=list, description="Interview questions")
    answers: List[InterviewResponse] = Field(default_factory=list, description="Interview answers")
    scheduled_at: Optional[datetime] = Field(default=None, description="Scheduled start time")
    started_at: Optional[datetime] = Field(default=None, description="Actual start time")
    completed_at: Optional[datetime] = Field(default=None, description="Completion time")
    duration: Optional[int] = Field(default=None, description="Total duration in seconds")
    score: Optional[float] = Field(default=None, description="Overall interview score", ge=0.0, le=100.0)
    feedback: Optional[str] = Field(default=None, description="Interview feedback")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    observers: Optional[List[Dict[str, Any]]] = Field(default=None, description="Observer configurations")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra='allow'
    )

    def start(self) -> None:
        """Start the interview."""
        if self.state != InterviewState.PENDING:
            raise ValueError("Interview can only be started when in PENDING state")
        
        self.state = InterviewState.ACTIVE
        self.started_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def complete(self) -> None:
        """Complete the interview."""
        if self.state != InterviewState.ACTIVE:
            raise ValueError("Interview can only be completed when in ACTIVE state")
        
        self.state = InterviewState.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.duration = int((self.completed_at - self.started_at).total_seconds())
        self.updated_at = datetime.now(timezone.utc)

    def fail(self) -> None:
        """Mark interview as failed."""
        if self.state == InterviewState.COMPLETED:
            raise ValueError("Cannot fail completed interview")
        
        self.state = InterviewState.FAILED
        self.completed_at = datetime.now(timezone.utc)
        self.duration = int((self.completed_at - self.started_at).total_seconds())
        self.updated_at = datetime.now(timezone.utc)

    def add_answer(self, answer: InterviewResponse) -> None:
        """Add an answer to the interview."""
        if self.state != InterviewState.ACTIVE:
            raise ValueError("Can only add answers to active interview")
        
        self.answers.append(answer)
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert interview to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "flow_id": self.flow_id,
            "title": self.title,
            "description": self.description,
            "state": self.state.value,
            "flow": self.flow.dict(),
            "questions": [q.dict() for q in self.questions],
            "answers": [a.dict() for a in self.answers],
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration": self.duration,
            "score": self.score,
            "feedback": self.feedback,
            "metadata": self.metadata,
            "observers": self.observers,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class InterviewMetrics(CoreBaseModel):
    """Interview metrics for admin overview."""
    total_interviews: int = Field(default=0, description="Total number of interviews")
    completed_interviews: int = Field(default=0, description="Number of completed interviews")
    active_interviews: int = Field(default=0, description="Number of active interviews")
    average_duration_minutes: float = Field(default=0.0, description="Average interview duration in minutes")
    completion_rate: float = Field(default=0.0, description="Interview completion rate")
    average_score: float = Field(default=0.0, description="Average interview score")
    total_questions: int = Field(default=0, description="Total number of questions")
    total_answers: int = Field(default=0, description="Total number of answers")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metrics") 