"""Core interview type definitions."""
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone
from uuid import UUID
from enum import Enum
from pydantic import Field, model_validator, field_validator, ConfigDict
from core.types.model import CoreBaseModel
from core.types.session import SessionType, SessionState

class InterviewState(str, Enum):
    """Interview session states."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class InterviewType(str, Enum):
    """Interview types."""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    MIXED = "mixed"

class InterviewMode(str, Enum):
    """Interview modes."""
    MOCK = "mock"  # Mock interview for job preparation
    EVALUATION = "evaluation"  # Course evaluation
    INFORMATION = "information"  # Information gathering
    STATUS = "status"  # Work status recording

class InterviewRole(str, Enum):
    """Interview roles."""
    INTERVIEWER = "interviewer"  # LLM acts as interviewer
    INTERVIEWEE = "interviewee"  # LLM acts as interviewee
    MEDIATOR = "mediator"  # LLM acts as mediator/support

class InterviewScore(CoreBaseModel):
    """Interview response score."""
    value: float = Field(..., description="Numerical score (0-100)")
    category: str = Field(..., description="Score category")
    criteria: Dict[str, float] = Field(..., description="Scoring criteria breakdown")
    confidence: float = Field(..., description="Confidence in the score (0-1)")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class InterviewFeedback(CoreBaseModel):
    """Interview feedback."""
    strengths: List[str] = Field(..., description="List of strengths")
    improvements: List[str] = Field(..., description="List of areas for improvement")
    suggestions: List[str] = Field(..., description="List of suggestions")
    overall_assessment: str = Field(..., description="Overall assessment")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class InterviewQuestion(CoreBaseModel):
    """Interview question."""
    id: str = Field(..., description="Question ID")
    content: str = Field(..., description="Question content")
    type: str = Field(..., description="Question type")
    difficulty: str = Field(..., description="Question difficulty")
    category: str = Field(..., description="Question category")
    expected_duration: int = Field(..., description="Expected duration in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class InterviewResponse(CoreBaseModel):
    """Interview response with analysis."""
    id: str = Field(..., description="Response ID")
    question_id: str = Field(..., description="Associated question ID")
    content: str = Field(..., description="Response content")
    score: InterviewScore = Field(..., description="Response score")
    feedback: InterviewFeedback = Field(..., description="Response feedback")
    duration: float = Field(..., description="Response duration in seconds")
    created_at: datetime = Field(..., description="Response timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class InterviewStep(CoreBaseModel):
    """Interview flow step."""
    id: str = Field(..., description="Step ID")
    type: str = Field(..., description="Step type")
    question: InterviewQuestion = Field(..., description="Step question")
    expected_duration: int = Field(..., description="Expected duration in seconds")
    dependencies: List[str] = Field(default_factory=list, description="Dependent step IDs")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Progression conditions")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class InterviewFlowConfig(CoreBaseModel):
    """Interview flow configuration model."""
    
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

class InterviewFlow(CoreBaseModel):
    """Interview flow model."""
    
    id: str = Field(description="Flow ID")
    name: str = Field(description="Flow name")
    description: str = Field(description="Flow description")
    config: InterviewFlowConfig = Field(description="Flow configuration")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @classmethod
    def get_default_flow(cls, flow_id: str) -> 'InterviewFlow':
        """Get default flow configuration.
        
        Args:
            flow_id: Flow identifier
            
        Returns:
            Default flow configuration
        """
        return cls(
            id=flow_id,
            name="Default Interview Flow",
            description="Default interview flow configuration",
            config=InterviewFlowConfig(
                mode=InterviewMode.MOCK,
                role=InterviewRole.INTERVIEWER,
                type=InterviewType.TECHNICAL,
                max_duration=3600,  # 1 hour
                max_questions=20,
                min_response_words=10,
                evaluation_metrics=[
                    "relevance",
                    "clarity",
                    "depth",
                    "accuracy",
                    "confidence"
                ],
                question_prompt="Generate a {difficulty} {category} question for {mode} interview.",
                answer_prompt="Analyze the following answer for {mode} interview: {answer}",
                feedback_prompt="Generate feedback for {mode} interview with {question_count} questions."
            )
        )

class Question(CoreBaseModel):
    """Interview question model."""
    
    content: str = Field(description="Question content")
    type: str = Field(description="Question type")
    category: str = Field(description="Question category")
    difficulty: str = Field(description="Question difficulty")
    expected_duration: int = Field(description="Expected duration in seconds", gt=0)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        """Validate difficulty level.
        
        Args:
            v: Difficulty value to validate
            
        Returns:
            Validated difficulty value
            
        Raises:
            ValueError: If difficulty is invalid
        """
        valid_levels = ['easy', 'medium', 'hard', 'expert']
        if v.lower() not in valid_levels:
            raise ValueError(f'Difficulty must be one of {valid_levels}')
        return v.lower()

class Answer(CoreBaseModel):
    """Interview answer model."""
    
    question_id: UUID = Field(description="Question ID")
    content: str = Field(description="Answer content")
    duration: int = Field(description="Answer duration in seconds", gt=0)
    confidence_score: float = Field(description="Answer confidence score", ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate answer content.
        
        Args:
            v: Content to validate
            
        Returns:
            Validated content
            
        Raises:
            ValueError: If content is empty
        """
        if not v.strip():
            raise ValueError('Answer content cannot be empty')
        return v.strip()

class Interview(CoreBaseModel):
    """Interview model."""
    
    id: UUID = Field(description="Interview ID")
    user_id: UUID = Field(description="User ID")
    flow_id: str = Field(description="Interview flow ID")
    session_id: Optional[UUID] = Field(default=None, description="Associated session ID")
    title: str = Field(description="Interview title")
    description: str = Field(description="Interview description")
    state: InterviewState = Field(default=InterviewState.PENDING, description="Interview state")
    session_type: SessionType = Field(default=SessionType.INTERVIEW, description="Session type")
    flow: InterviewFlow = Field(description="Interview flow configuration")
    questions: List[Question] = Field(default_factory=list, description="Interview questions")
    answers: List[Answer] = Field(default_factory=list, description="Interview answers")
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
    
    @model_validator(mode='after')
    def validate_timestamps(self) -> 'Interview':
        """Validate timestamp sequence."""
        if self.scheduled_at and self.started_at:
            if self.started_at < self.scheduled_at:
                raise ValueError("Start time cannot be before scheduled time")
        if self.started_at and self.completed_at:
            if self.completed_at < self.started_at:
                raise ValueError("Completion time cannot be before start time")
        return self
    
    def add_question(self, question: Question) -> None:
        """Add question to interview.
        
        Args:
            question: Question to add
        """
        self.questions.append(question)
        self.updated_at = datetime.now(timezone.utc)
        
    def add_answer(self, answer: Answer) -> None:
        """Add answer to interview.
        
        Args:
            answer: Answer to add
        """
        if not any(q.id == answer.question_id for q in self.questions):
            raise ValueError("Answer must correspond to an existing question")
        self.answers.append(answer)
        self.updated_at = datetime.now(timezone.utc)

class InterviewSession(CoreBaseModel):
    """Interview session state."""
    id: str = Field(..., description="Session ID")
    flow_id: str = Field(..., description="Associated flow ID")
    trainee_id: str = Field(..., description="Trainee ID")
    state: InterviewState = Field(..., description="Session state")
    current_step: Optional[str] = Field(None, description="Current step ID")
    completed_steps: List[str] = Field(default_factory=list, description="Completed step IDs")
    responses: Dict[str, InterviewResponse] = Field(default_factory=dict, description="Step responses")
    start_time: datetime = Field(..., description="Session start time")
    end_time: Optional[datetime] = Field(None, description="Session end time")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class InterviewAnalysis(CoreBaseModel):
    """Overall interview analysis."""
    session_id: str = Field(..., description="Session ID")
    overall_score: float = Field(..., description="Overall interview score")
    score_breakdown: Dict[str, float] = Field(..., description="Score breakdown by category")
    key_strengths: List[str] = Field(..., description="Key strengths across interview")
    key_improvements: List[str] = Field(..., description="Key areas for improvement")
    recommendations: List[str] = Field(..., description="Specific recommendations")
    duration: float = Field(..., description="Total interview duration")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class InterviewEvent(CoreBaseModel):
    """Interview session event."""
    id: str = Field(..., description="Event ID")
    session_id: str = Field(..., description="Session ID")
    type: str = Field(..., description="Event type")
    step_id: Optional[str] = Field(None, description="Related step ID")
    data: Dict[str, Any] = Field(..., description="Event data")
    timestamp: datetime = Field(..., description="Event timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict) 