"""Interview API models."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import Field
from uuid import UUID

from core.types.model import CoreBaseModel


class QuestionCreateDTO(CoreBaseModel):
    """Question creation request DTO."""
    content: str = Field(description="Question content")
    category: str = Field(description="Question category")
    difficulty: int = Field(description="Question difficulty (1-5)")
    metadata: Optional[Dict] = Field(default=None, description="Additional metadata")


class QuestionResponseDTO(CoreBaseModel):
    """Question response DTO."""
    id: UUID = Field(description="Question ID")
    interview_id: UUID = Field(description="Interview ID")
    content: str = Field(description="Question content")
    category: str = Field(description="Question category")
    difficulty: int = Field(description="Question difficulty")
    status: str = Field(description="Question status")
    score: Optional[float] = Field(None, description="Question score")
    feedback: Optional[str] = Field(None, description="Question feedback")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class InterviewCreateDTO(CoreBaseModel):
    """Interview creation request DTO."""
    title: str = Field(description="Interview title")
    description: Optional[str] = Field(None, description="Interview description")
    job_id: UUID = Field(description="Job ID")
    metadata: Optional[Dict] = Field(None, description="Additional metadata")


class InterviewUpdateDTO(CoreBaseModel):
    """Interview update request DTO."""
    title: Optional[str] = Field(None, description="Interview title")
    description: Optional[str] = Field(None, description="Interview description")
    status: Optional[str] = Field(None, description="Interview status")
    metadata: Optional[Dict] = Field(None, description="Additional metadata")


class InterviewResponseDTO(CoreBaseModel):
    """Interview response DTO."""
    id: UUID = Field(description="Interview ID")
    user_id: UUID = Field(description="User ID")
    job_id: UUID = Field(description="Job ID")
    title: str = Field(description="Interview title")
    description: str = Field(description="Interview description")
    status: str = Field(description="Interview status")
    total_questions: int = Field(description="Total number of questions")
    completed_questions: int = Field(description="Number of completed questions")
    average_score: Optional[float] = Field(None, description="Average score")
    duration: Optional[int] = Field(None, description="Duration in seconds")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")
    questions: List[QuestionResponseDTO] = Field(default_factory=list, description="Interview questions")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class InterviewFeedbackDTO(CoreBaseModel):
    """Interview feedback DTO."""
    interview_id: UUID = Field(description="Interview ID")
    overall_score: float = Field(description="Overall interview score")
    strengths: List[str] = Field(description="Areas of strength")
    improvements: List[str] = Field(description="Areas for improvement")
    feedback: str = Field(description="Detailed feedback")
    recommendations: List[str] = Field(description="Recommendations")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata") 