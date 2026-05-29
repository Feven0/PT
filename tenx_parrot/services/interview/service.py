"""Interview service implementation."""
from typing import Dict, List, Optional, Set, Union, Any
from datetime import datetime, timezone
from uuid import UUID
import asyncio

from core.base.service import BaseService
from core.config.base import AppConfig
from core.alert.manager import AlertManager
from core.telemetry.metrics import MetricsManager
from core.errors.handlers import NotFoundError, ValidationError, handle_errors
from core.resilience import circuit_breaker, retry, timeout
from core.logging import BackendLogger
from core.types.metrics import MetricType
from core.types.components import HealthStatus, HealthStatusInfo, ComponentState
from core.websocket.socketio_manager import SocketIOManager
from core.types.websocket import (
    SocketEvent,
    SocketEventData
)
from core.types.interview import (
    InterviewState,
    InterviewScore,
    InterviewFeedback,
    InterviewType,
    InterviewMode,
    InterviewRole,
    Interview,
    Question,
    Answer,
    InterviewFlow,
    InterviewFlowConfig
)
from core.types.rubric import Rubric
from core.types.session import (
    Session,
    SessionState,
    SessionType
)
from core.types.analysis import (
    AnalysisResult,
    AnalysisType,
    AnalysisStatus
)
from core.types.audio import (
    AudioInterview,
    AudioQuality,
    AudioFormat,
    AudioChunk
)
from core.types.transcript import (
    Transcript,
    SpeakerType,
    TranscriptSegment
)


from services.llm.interview.service import InterviewLLMService
from services.session.service import SessionManagementService
from services.observer.service import ObserverService


class InterviewService(BaseService):
    """Service for managing interviews."""
    
    REQUIRED_CONFIG = {
        "max_duration": int,
        "max_questions": int,
        "max_retries": int,
        "batch_size": int,
        "cache_ttl": int,
        "max_concurrent": int,        
        'min_response_words': int,
        'evaluation_metrics': List[str]
    }
    
    def __init__(
        self,
        name: str,
        config: AppConfig,
        session_service: SessionManagementService,
        interview_llm_service: InterviewLLMService,
        observer_service: ObserverService,
        socketio_manager: SocketIOManager,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None,
    ):
        """Initialize interview service.
        
        Args:
            name: Service name
            config: Application configuration
            session_service: Session management service
            interview_llm_service: Interview LLM service
            observer_service: Observer service
            metrics: Metrics collector (optional)
            logger: Optional logger instance
            dependencies: Optional set of dependency names
        """
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies,
            REQUIRED_CONFIG=self.REQUIRED_CONFIG
        )
        
        self.socketio_manager = socketio_manager
        self.session_service = session_service
        self.interview_llm_service = interview_llm_service
        self.observer_service = observer_service
        
        # Get validated config
        config_dict = self._config
        
        # Initialize interview settings from validated config with defaults
        self._max_duration = config_dict.get("max_duration", 3600)  # 1 hour default
        self._max_questions = config_dict.get("max_questions", 20)
        self._max_retries = config_dict.get("max_retries", 3)
        self._batch_size = config_dict.get("batch_size", 100)
        self._cache_ttl = config_dict.get("cache_ttl", 3600)
        self._max_concurrent = config_dict.get("max_concurrent", 5)
        self._min_response_words = config_dict.get("min_response_words", 10)
        self._evaluation_metrics = config_dict.get("evaluation_metrics", [
            "relevance",
            "clarity",
            "depth",
            "accuracy",
            "confidence"
        ])
        
        # Initialize health status
        self._health_status = HealthStatusInfo(
            status=HealthStatus.STARTING,
            details={
                "status": "initializing",
                "component": self.name,
                "config": {
                    "max_duration": self._max_duration,
                    "max_questions": self._max_questions,
                    "max_retries": self._max_retries,
                    "batch_size": self._batch_size
                },
                "metrics": {
                    "active_interviews": 0,
                    "questions_processed": 0,
                    "errors": 0
                }
            }
        )
        
        # Register metrics if available
        if self.metrics:
            self._register_metrics()
            
        # Register socket event handlers
        self._register_handlers()
        
        # Initialize interview state
        self._active_interviews: Dict[str, Dict] = {}
        self._interview_history: List[Dict] = []
        self._lock = asyncio.Lock()

    def _register_metrics(self) -> None:
        """Register service metrics."""
        # Operation Metrics
        self.metrics.register_metric(
            f"{self.name}_operations_total",
            MetricType.COUNTER,
            f"Total number of operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Performance Metrics
        self.metrics.register_metric(
            f"{self.name}_operation_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Interview Metrics
        self.metrics.register_metric(
            f"{self.name}_interviews_total",
            MetricType.COUNTER,
            f"Total number of interviews in {self.name}",
            labels={"status": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_active_interviews",
            MetricType.GAUGE,
            f"Number of active interviews in {self.name}"
        )
        
        self.metrics.register_metric(
            f"{self.name}_interview_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of interviews in {self.name}",
            labels={"status": ""}
        )
        
        # Question Metrics
        self.metrics.register_metric(
            f"{self.name}_questions_total",
            MetricType.COUNTER,
            f"Total number of questions in {self.name}",
            labels={"type": "", "status": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_question_generation_time_seconds",
            MetricType.HISTOGRAM,
            f"Time taken to generate questions in {self.name}"
        )
        
        # Response Metrics
        self.metrics.register_metric(
            f"{self.name}_responses_total",
            MetricType.COUNTER,
            f"Total number of responses in {self.name}",
            labels={"status": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_response_analysis_time_seconds",
            MetricType.HISTOGRAM,
            f"Time taken to analyze responses in {self.name}"
        )
        
        self.metrics.register_metric(
            f"{self.name}_response_scores",
            MetricType.GAUGE,
            f"Response evaluation scores in {self.name}",
            labels={"metric": "", "interview_id": ""}
        )
        
        # Error Metrics
        self.metrics.register_metric(
            f"{self.name}_errors_total",
            MetricType.COUNTER,
            f"Total number of errors in {self.name}",
            labels={"error_type": "", "operation": ""}
        )

    def _register_handlers(self) -> None:
        """Register socket event handlers."""
        self.socketio_manager.register_handler(
            SocketEvent.INTERVIEW_START,
            self._handle_interview_start
        )
        self.socketio_manager.register_handler(
            SocketEvent.INTERVIEW_QUESTION,
            self._handle_interview_question
        )
        self.socketio_manager.register_handler(
            SocketEvent.INTERVIEW_ANSWER,
            self._handle_interview_answer
        )

    async def _handle_interview_start(self, event: SocketEventData) -> None:
        """Handle interview start event."""
        try:
            data = event.data
            session_id = event.room
            user_id = data.get("user_id")
            flow_id = data.get("flow_id")
            title = data.get("title", f"Interview - {user_id}")

            if not all([session_id, user_id, flow_id]):
                raise ValueError("Missing required fields for interview start")

            # Create interview session
            interview = await self.create_interview(Interview(
                id=session_id,
                user_id=user_id,
                flow_id=flow_id,
                title=title,
                description=data.get("description", ""),
                state=InterviewState.PENDING,
                metadata={
                    "flow_id": flow_id,
                    "started_at": datetime.now(timezone.utc).isoformat()
                }
            ))

            # Broadcast session state
            await self.socketio_manager.broadcast_state_change(
                {
                    "session_id": session_id,
                    "state": InterviewState.STARTED,
                    "metadata": {
                        "user_id": user_id,
                        "flow_id": flow_id,
                        "started_at": datetime.now(timezone.utc).isoformat()
                    }
                },
                room=session_id
            )

        except Exception as e:
            self.logger.error(f"Error handling interview start: {str(e)}")
            raise

    async def _handle_interview_question(self, event: SocketEventData) -> None:
        """Handle interview question event."""
        try:
            data = event.data
            session_id = event.room

            if not session_id:
                raise ValueError("Session ID required")

            # Get session
            session = await self.get_interview(session_id)
            if not session:
                raise ValueError(f"Interview session {session_id} not found")

            # Generate question
            question_data = await self.generate_question(
                session=session,
                context=data.get("context", {})
            )

            # Broadcast question
            await self.socketio_manager.emit(
                SocketEvent.INTERVIEW_QUESTION,
                {
                    "session_id": session_id,
                    "question": question_data["question"],
                    "metadata": question_data["metadata"]
                },
                room=session_id
            )

        except Exception as e:
            self.logger.error(f"Error handling interview question: {str(e)}")
            raise

    async def _handle_interview_answer(self, event: SocketEventData) -> None:
        """Handle interview answer event."""
        try:
            data = event.data
            session_id = event.room
            answer = data.get("answer")

            if not all([session_id, answer]):
                raise ValueError("Missing required fields for interview answer")

            # Get session
            session = await self.get_interview(session_id)
            if not session:
                raise ValueError(f"Interview session {session_id} not found")

            # Validate response
            if not await self.validate_response(answer):
                await self.socketio_manager.emit(
                    SocketEvent.ERROR,
                    {
                        "error": "Invalid response",
                        "details": f"Response must be at least {self._min_response_words} words"
                    },
                    room=session_id
                )
                return

            # Analyze response
            analysis = await self.analyze_response(
                session=session,
                response=answer,
                context=data.get("context", {})
            )

            # Broadcast analysis
            await self.socketio_manager.emit(
                SocketEvent.INTERVIEW_ANSWER,
                {
                    "session_id": session_id,
                    "answer": answer,
                    "analysis": analysis,
                    "metadata": {
                        "question": session.data["questions"][-1],
                        "analyzed_at": datetime.now(timezone.utc).isoformat()
                    }
                },
                room=session_id
            )

            # Check if interview is complete
            if await self.is_interview_complete(session):
                # Generate feedback
                feedback = await self.generate_feedback(
                    session=session,
                    context=data.get("context", {})
                )

                # Complete interview
                await self.complete_interview(session_id)

                # Broadcast completion
                await self.socketio_manager.broadcast_state_change(
                    {
                        "session_id": session_id,
                        "state": InterviewState.COMPLETED,
                        "metadata": {
                            "completed_at": datetime.now(timezone.utc).isoformat(),
                            "feedback": feedback
                        }
                    },
                    room=session_id
                )

        except Exception as e:
            self.logger.error(f"Error handling interview answer: {str(e)}")
            raise

    @handle_errors(ValidationError, "Failed to validate interview")
    async def validate_interview(self, interview: Interview) -> None:
        """Validate interview configuration.
        
        Args:
            interview: Interview to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not interview.user_id:
            raise ValidationError(
                "Interview must have user ID",
                details={"field": "user_id"}
            )
            
        if not interview.flow_id:
            raise ValidationError(
                "Interview must have flow ID",
                details={"field": "flow_id"}
            )
            
    @circuit_breaker(name="create_interview")
    @retry(attempts=3, delay=1.0)
    @timeout(30.0)
    async def create_interview(self, interview: Interview) -> Interview:
        """Create a new interview.
        
        Args:
            interview: Interview to create
            
        Returns:
            Created interview
        """
        try:
            # Validate interview
            await self.validate_interview(interview)
            
            # Prepare metadata
            metadata = interview.to_session_metadata()
            metadata.update({
                "max_questions": self._max_questions,
                "max_duration": self._max_duration,
                "evaluation_metrics": self._evaluation_metrics
            })
            
            # Create session
            session = await self.session_service.create_session(
                user_id=str(interview.user_id),
                session_type=SessionType.INTERVIEW,
                title=interview.title,
                metadata=metadata,
                data=interview.to_session_data()
            )
            
            # Update interview with session ID
            interview.session_id = session.id
            interview.created_at = session.created_at
            interview.state = InterviewState.CREATED
            
            # Create observers for this interview
            if interview.observers:
                for observer_config in interview.observers:
                    await self.observer_service.create_observer(
                        session_id=session.id,
                        observer_config=observer_config
                    )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_interviews_total",
                    1,
                    labels={"status": "created"}
                )
                self.metrics.record(
                    f"{self.name}_active_interviews",
                    1
                )
            
            # Emit event
            await self.socketio_manager.emit(
                SocketEvent.INTERVIEW_CREATED,
                {
                    "session_id": str(session.id),
                    "user_id": str(interview.user_id),
                    "interview_type": interview.interview_type,
                    "created_at": interview.created_at.isoformat()
                },
                room=str(session.id)
            )
            
            return interview
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "create_interview"}
                )
            self.logger.error(f"Failed to create interview: {str(e)}")
            raise

    @circuit_breaker(name="get_interview")
    @retry(attempts=3, delay=1.0)
    @timeout(10.0)
    async def get_interview(self, session_id: str) -> Optional[Interview]:
        """Get interview by session ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Interview if found
        """
        session = await self.session_service.get_session(session_id)
        
        if not session:
            raise NotFoundError(
                "Interview not found",
                resource_type="interview",
                resource_id=session_id
            )
            
        return Interview.from_session(session)
        
    @circuit_breaker(name="list_interviews")
    @retry(attempts=3, delay=1.0)
    @timeout(30.0)
    async def list_interviews(
        self,
        page: int = 1,
        page_size: int = 10
    ) -> List[Interview]:
        """List interviews with pagination.
        
        Args:
            page: Page number
            page_size: Items per page
            
        Returns:
            List of interviews
        """
        sessions = await self.session_service.list_sessions(
            session_type=SessionType.INTERVIEW,
            page=page,
            page_size=page_size
        )
        
        return [Interview.from_session(session) for session in sessions]
        
    @circuit_breaker(name="update_interview")
    @retry(attempts=3, delay=1.0)
    @timeout(30.0)
    async def update_interview(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Interview]:
        """Update interview.
        
        Args:
            session_id: Session identifier
            updates: Fields to update
            
        Returns:
            Updated interview if found
        """
        # Get interview
        interview = await self.get_interview(session_id)
        if not interview:
            return None
            
        # Update state
        success = await self.session_service.update_session_state(
            session_id,
            updates
        )
        
        if not success:
            raise ValidationError(
                "Failed to update interview",
                details={"session_id": session_id}
            )
            
        return interview
        
    @circuit_breaker(name="complete_interview")
    @retry(attempts=3, delay=1.0)
    @timeout(30.0)
    async def complete_interview(self, session_id: str) -> None:
        """Complete interview.
        
        Args:
            session_id: Session identifier
        """
        # Get interview
        interview = await self.get_interview(session_id)
        if not interview:
            return
            
        # Complete session
        await self.session_service.complete_session(session_id)
        
        # Update metrics
        if self.metrics:
            self.metrics.record(
                f"{self.name}_interviews_total",
                1,
                labels={"status": "completed"}
            )
            self.metrics.record(
                f"{self.name}_active_interviews",
                -1
            )
        
        self.logger.info(
            "interview_completed",
            context="interview",
            session_id=session_id
        )
        
    @circuit_breaker(name="handle_interruption")
    @retry(attempts=3, delay=1.0)
    async def handle_interruption(
        self,
        session_id: str,
        reason: str
    ) -> None:
        """Handle interview interruption.
        
        Args:
            session_id: Session identifier
            reason: Interruption reason
        """
        # Get interview
        interview = await self.get_interview(session_id)
        if not interview:
            return
            
        # Handle interruption
        await self.session_service.handle_interruption(session_id, reason)
        
        # Update metrics
        if self.metrics:
            self.metrics.record(
                f"{self.name}_interviews_total",
                1,
                labels={"status": "interrupted"}
            )
        
        self.logger.warning(
            "interview_interrupted",
            context="interview",
            session_id=session_id,
            reason=reason
        )

    async def generate_question(
        self,
        session: Session,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate next interview question.
        
        Args:
            session: Interview session
            context: Additional context
            
        Returns:
            Generated question data
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            # Get interview with flow configuration
            interview = Interview.from_session(session)
            flow_config = interview.flow.config
            
            # Get question generation prompt template
            prompt_template = flow_config.question_prompt
            
            # Add session context
            context.update({
                "session_id": session.id,
                "question_count": len(session.data.get("questions", [])),
                "previous_answers": session.data.get("answers", []),
                "evaluation_metrics": flow_config.evaluation_metrics,
                "mode": flow_config.mode.value,
                "role": flow_config.role.value,
                "type": flow_config.type.value
            })
            
            # Generate question based on role
            if flow_config.role == InterviewRole.INTERVIEWER:
                # LLM acts as interviewer
                response = await self.interview_llm_service.generate_interview_response(
                    session_id=session.id,
                    user_message=prompt_template.format(**context),
                    context=context
                )
                
                # Create question model
                question = Question(
                    content=response.text,
                    type=context.get("type", "technical"),
                    category=context.get("category", "programming"),
                    difficulty=context.get("difficulty", "medium"),
                    expected_duration=context.get("duration", 300),
                    metadata={
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "context": context,
                        "metrics": response.metadata.get("metrics", {}),
                        "role": flow_config.role.value
                    }
                )
                
            elif flow_config.role == InterviewRole.INTERVIEWEE:
                # LLM acts as interviewee
                response = await self.interview_llm_service.generate_interview_response(
                    session_id=session.id,
                    user_message="Generate a response to the user's question.",
                    context=context
                )
                
                # Create answer model
                answer = Answer(
                    question_id=context.get("question_id"),
                    content=response.text,
                    duration=int((datetime.now(timezone.utc) - start_time).total_seconds()),
                    confidence_score=response.metadata.get("confidence", 0.0),
                    metadata={
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "context": context,
                        "metrics": response.metadata.get("metrics", {}),
                        "role": flow_config.role.value
                    }
                )
                
                # Update session data
                if "answers" not in session.data:
                    session.data["answers"] = []
                session.data["answers"].append(answer.dict())
                
                return answer.dict()
                
            else:  # MEDIATOR
                # LLM acts as mediator
                response = await self.interview_llm_service.generate_interview_response(
                    session_id=session.id,
                    user_message="Generate a suggestion or hint for the interview.",
                    context=context
                )
                
                # Create suggestion model
                suggestion = {
                    "content": response.text,
                    "type": "suggestion",
                    "metadata": {
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "context": context,
                        "metrics": response.metadata.get("metrics", {}),
                        "role": flow_config.role.value
                    }
                }
                
                return suggestion
            
            # Update session data
            if "questions" not in session.data:
                session.data["questions"] = []
            session.data["questions"].append(question.dict())
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_questions_total",
                    1,
                    labels={
                        "type": flow_config.type.value,
                        "role": flow_config.role.value,
                        "status": "success"
                    }
                )
                self.metrics.record(
                    f"{self.name}_question_generation_time_seconds",
                    (datetime.now(timezone.utc) - start_time).total_seconds()
                )
            
            return question.dict()
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={
                        "error_type": type(e).__name__,
                        "operation": "generate_question"
                    }
                )
                self.metrics.record(
                    f"{self.name}_questions_total",
                    1,
                    labels={
                        "type": flow_config.type.value,
                        "role": flow_config.role.value,
                        "status": "error"
                    }
                )
            self.logger.error(f"Failed to generate question: {str(e)}")
            raise

    async def _stream_response(
        self,
        session_id: str,
        response_data: Dict[str, Any]
    ) -> None:
        """Stream response data to client.
        
        Args:
            session_id: Session identifier
            response_data: Response data to stream
        """
        try:
            # Get interview with flow configuration
            session = await self.get_interview(session_id)
            flow_config = session.flow.config
            stream_config = flow_config.streaming_config
            
            # Check if streaming is enabled and appropriate
            if not stream_config.get("enabled", False):
                return
                
            # Check if response is streamable
            content = response_data.get("content", "")
            if not content or not isinstance(content, str):
                return
                
            # Check if response is from LLM chain streaming
            is_llm_stream = response_data.get("metadata", {}).get("stream_source") == "llm"
            
            if is_llm_stream:
                # For LLM streaming, emit chunks as they arrive
                chunk_data = {
                    "session_id": session_id,
                    "chunk": content,
                    "metadata": {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "stream_source": "llm"
                    }
                }
                
                # Add additional metadata if enabled
                if stream_config.get("include_metadata", True):
                    chunk_data["metadata"].update({
                        "metrics": response_data.get("metadata", {}).get("metrics", {}),
                        "feedback": response_data.get("metadata", {}).get("feedback", [])
                    })
                
                # Emit chunk
                await self.socketio_manager.emit(
                    SocketEvent.INTERVIEW_RESPONSE_CHUNK,
                    chunk_data,
                    room=session_id
                )
                
            else:
                # For non-streaming responses, emit complete response
                response_data["metadata"].update({
                    "stream_source": "complete",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
                await self.socketio_manager.emit(
                    SocketEvent.INTERVIEW_RESPONSE_COMPLETE,
                    response_data,
                    room=session_id
                )
            
        except Exception as e:
            self.logger.error(f"Failed to stream response: {str(e)}")
            raise

    async def analyze_response(
        self,
        session: Session,
        response: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze candidate response.
        
        Args:
            session: Interview session
            response: Candidate response
            context: Additional context
            
        Returns:
            Analysis result
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            # Get interview with flow configuration
            interview = Interview.from_session(session)
            flow_config = interview.flow.config
            
            # Get answer analysis prompt template
            prompt_template = flow_config.answer_prompt
            
            # Add session context
            context.update({
                "session_id": session.id,
                "response": response,
                "question": session.data["questions"][-1]["content"],
                "evaluation_metrics": flow_config.evaluation_metrics,
                "mode": flow_config.mode.value,
                "role": flow_config.role.value,
                "type": flow_config.type.value
            })
            
            # Get rubric
            rubric_id = flow_config.rubric_id
            rubric = Rubric.get_default_rubric(rubric_id) if rubric_id else None
            
            # Generate analysis with streaming if enabled
            stream_config = flow_config.streaming_config
            is_streaming = stream_config.get("enabled", False)
            
            analysis = await self.interview_llm_service.generate_interview_response(
                session_id=session.id,
                user_message=prompt_template.format(**context),
                context=context,
                stream=is_streaming
            )
            
            # Process analysis with rubric if available
            metrics = {}
            feedback = []
            
            if rubric:
                for metric in rubric.metrics:
                    # Get metric score from analysis
                    score = analysis.metadata.get("metrics", {}).get(metric.name, 0.0)
                    
                    # Determine score level
                    score_level = "poor"
                    for level, threshold in metric.score_range.items():
                        if score >= threshold:
                            score_level = level
                            break
                    
                    # Generate feedback for this metric
                    metric_feedback = metric.feedback_template.format(
                        score_level=score_level,
                        feedback=analysis.metadata.get("feedback", {}).get(metric.name, "")
                    )
                    
                    metrics[metric.name] = {
                        "score": score,
                        "weight": metric.weight,
                        "level": score_level,
                        "feedback": metric_feedback
                    }
                    feedback.append(metric_feedback)
            
            # Create answer model
            answer = Answer(
                question_id=session.data["questions"][-1]["id"],
                content=response,
                duration=int((datetime.now(timezone.utc) - start_time).total_seconds()),
                confidence_score=analysis.metadata.get("confidence", 0.0),
                metadata={
                    "analyzed_at": datetime.now(timezone.utc).isoformat(),
                    "context": context,
                    "metrics": metrics,
                    "feedback": feedback,
                    "role": flow_config.role.value,
                    "stream_source": "llm" if is_streaming else "complete"
                }
            )
            
            # Update session data
            if "answers" not in session.data:
                session.data["answers"] = []
            session.data["answers"].append(answer.dict())
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_responses_total",
                    1,
                    labels={
                        "type": flow_config.type.value,
                        "role": flow_config.role.value,
                        "status": "success"
                    }
                )
                self.metrics.record(
                    f"{self.name}_response_analysis_time_seconds",
                    (datetime.now(timezone.utc) - start_time).total_seconds()
                )
                
                # Record individual metric scores
                for metric_name, metric_data in metrics.items():
                    self.metrics.record(
                        f"{self.name}_response_scores",
                        metric_data["score"],
                        labels={
                            "metric": metric_name,
                            "interview_id": str(session.id),
                            "level": metric_data["level"]
                        }
                    )
            
            # Handle response streaming
            await self._stream_response(session.id, answer.dict())
            
            return answer.dict()
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={
                        "error_type": type(e).__name__,
                        "operation": "analyze_response"
                    }
                )
                self.metrics.record(
                    f"{self.name}_responses_total",
                    1,
                    labels={
                        "type": flow_config.type.value,
                        "role": flow_config.role.value,
                        "status": "error"
                    }
                )
            self.logger.error(f"Failed to analyze response: {str(e)}")
            raise

    async def generate_feedback(
        self,
        session: Session,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate overall interview feedback.
        
        Args:
            session: Interview session
            context: Feedback context
            
        Returns:
            Feedback data
        """
        try:
            # Get feedback prompt
            prompt = await self.prompt_manager.get_prompt("interview_feedback")
            
            # Add session context
            context.update({
                "session_id": session.id,
                "questions": session.data.get("questions", []),
                "answers": session.data.get("answers", []),
                "evaluation_metrics": self._evaluation_metrics
            })
            
            # Generate feedback
            feedback = await self.interview_llm_service.generate_interview_response(
                session_id=session.id,
                user_message=prompt,
                context=context
            )
            
            # Extract feedback data
            feedback_data = {
                "summary": feedback.text,
                "metrics": feedback.metadata.get("metrics", {}),
                "recommendations": feedback.metadata.get("recommendations", []),
                "metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "context": context
                }
            }
            
            # Update session data
            session.data["feedback"] = feedback_data
            
            return feedback_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate feedback: {str(e)}")
            raise

    async def validate_response(self, response: str) -> bool:
        """Validate candidate response.
        
        Args:
            response: Candidate response
            
        Returns:
            Whether response is valid
        """
        if not response:
            return False
            
        # Check response length
        words = response.split()
        if len(words) < self._min_response_words:
            return False
            
        return True

    async def is_interview_complete(self, session: Session) -> bool:
        """Check if interview is complete.
        
        Args:
            session: Interview session
            
        Returns:
            Whether interview is complete
        """
        # Check question count
        questions = session.data.get("questions", [])
        if len(questions) >= self._max_questions:
            return True
            
        return False

    async def conduct_interview(
        self,
        session_id: str,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Conduct an interview interaction.
        
        Args:
            session_id: Interview session ID
            user_message: User message text
            context: Optional additional context
            
        Returns:
            Response containing generated text and metadata
        """
        try:
            # Store user message through session service
            await self.session_service.store_message(
                session_id=session_id,
                message={
                    "role": "user",
                    "content": user_message,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Use the LLM service to generate a response
            response = await self.interview_llm_service.generate_interview_response(
                session_id=session_id,
                user_message=user_message,
                context=context
            )
            
            # Additional interview-specific business logic can be added here
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to conduct interview: {e}")
            raise