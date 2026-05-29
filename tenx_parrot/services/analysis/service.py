"""Analysis service with lifecycle management."""
from typing import Dict, List, Optional, Set, Union, Any
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
from pydantic import Field
import asyncio

from core.base.service import BaseService
from core.config.base import AppConfig
from core.alert.manager import AlertManager
from core.telemetry.metrics import MetricsManager
from core.telemetry.decorators import track_component_operation
from core.cache.manager import CacheManager
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
from core.types.user import UserProfile
from core.types.analysis import (
    AnalysisResult,
    AnalysisMetric,
    AnalysisType,
    AnalysisStatus,
    QuestionStatus
)

from domain.models.analysis import (
    AnalysisDTO,
    AnalysisMetricsDTO
)
from core.types.user import UserProfile

from services.storage.service import StorageService
from services.interview.service import InterviewService
from services.session.service import SessionManagementService
from repositories.user import UserRepository
from repositories.analysis import AnalysisRepository


class AnalysisService(BaseService):
    """Service for managing interview analysis."""

    REQUIRED_CONFIG = {
        "cache_ttl": int,
        "batch_size": int,
        "max_retries": int
    }

    def __init__(
        self,
        name: str,
        config: AppConfig,        
        metrics: MetricsManager,
        alert_manager: AlertManager,
        cache_manager: CacheManager,
        interview_service: InterviewService,
        session_service: SessionManagementService,
        user_repository: UserRepository,
        analysis_repository: AnalysisRepository,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize the analysis service.
        
        Args:
            config: Application configuration
            logger: Logger instance
            metrics: Metrics manager
            alert_manager: Alert manager
            cache_manager: Cache manager
            storage_service: Storage service
            interview_service: Interview service
            session_service: Session management service
            user_repository: User repository
            analysis_repository: Analysis repository
        """
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies,
            required_config=self.REQUIRED_CONFIG
        )
        self.logger = logger
        self.metrics = metrics
        self.alert_manager = alert_manager
        self.cache_manager = cache_manager
        self.interview_service = interview_service
        self.session_service = session_service
        self.user_repository = user_repository
        self.analysis_repository = analysis_repository
        
        # Initialize cache
        self.cache = self.cache_manager
        self.cache_ttl = 300  # 5 minutes
        
        # Initialize analysis settings from validated config with defaults
        self._batch_size = self._config.get("batch_size", 100)
        self._max_retries = self._config.get("max_retries", 3)
        
        # Initialize health status
        self._health_status = HealthStatusInfo(
            status=HealthStatus.STARTING,
            details={
                "status": "initializing",
                "component": self.name,
                "config": {
                    "cache_ttl": self.cache_ttl,
                    "batch_size": self._batch_size,
                    "max_retries": self._max_retries
                },
                "metrics": {
                    "cached_stats": 0,
                    "analyses_performed": 0,
                    "cache_hits": 0,
                    "cache_misses": 0,
                    "errors": 0
                }
            }
        )

        # Register metrics
        self._register_metrics()


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
        
        # Analysis Metrics
        self.metrics.register_metric(
            f"{self.name}_analyzed_interviews_total",
            MetricType.COUNTER,
            f"Total number of interviews analyzed in {self.name}",
            labels={"type": "", "status": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_analysis_score",
            MetricType.GAUGE,
            f"Analysis score in {self.name}",
            labels={"interview_id": "", "metric": ""}
        )
        
        # Cache Metrics
        self.metrics.register_metric(
            f"{self.name}_cache_operations_total",
            MetricType.COUNTER,
            f"Total number of cache operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Error Metrics
        self.metrics.register_metric(
            f"{self.name}_errors_total",
            MetricType.COUNTER,
            f"Total number of errors in {self.name}",
            labels={"error_type": "", "operation": ""}
        )

    @track_component_operation("initialize")
    async def _initialize_impl(self) -> None:
        """Initialize analysis service."""
        try:                
            # Clear cached stats
            await self.cache.clear()
            
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "initialize", "status": "success"}
                )
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "initialize"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "initialize", "status": "error"}
                )
            raise

    @track_component_operation("start")
    async def _start_impl(self) -> None:
        """Start analysis service."""
        try:
                
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "start", "status": "success"}
                )
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "start"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "start", "status": "error"}
                )
            raise

    @track_component_operation("stop")
    async def _stop_impl(self) -> None:
        """Stop analysis service."""
        try:                
            # Clear cached stats
            await self.cache.clear()
            
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "stop", "status": "success"}
                )
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "stop"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "stop", "status": "error"}
                )
            raise
    
    async def _check_health_impl(self) -> HealthStatusInfo:
        """Check analysis service health."""
        health_info = HealthStatusInfo(
            status=HealthStatus.UNKNOWN,
            details={
                "metrics": {
                    "cached_stats": await self.cache.size()
                },
                "last_check": datetime.now()
            }
        )
        
        try:
            # Check dependencies
            interview_health = await self.interview_service.check_health()
            session_health = await self.session_service.check_health()
            
            # Determine health status based on dependencies
            if (
                interview_health["status"] == HealthStatus.UNHEALTHY or
                session_health["status"] == HealthStatus.UNHEALTHY):
                health_info.update(
                    status=HealthStatus.DEGRADED,
                    details={
                        **health_info.details,
                        "error": "One or more dependencies unhealthy"
                    }
                )
            else:
                health_info.status = HealthStatus.HEALTHY
            
            # Record metrics if available
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_cached_stats",
                    await self.cache.size(),
                    labels={"type": "total"}
                )
            
            return health_info
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            health_info.update(
                status=HealthStatus.UNHEALTHY,
                details={
                    **health_info.details,
                    "error": str(e)
                }
            )
            return health_info
    
    async def calculate_session_progress(self, session_id: UUID) -> float:
        """Calculate session progress percentage.
        
        Args:
            session_id: Session ID
            
        Returns:
            Progress percentage (0-100)
        """
        try:
            # Get session questions
            questions = await self.interview_service.get_session_questions(session_id)
            if not questions:
                return 0.0
            
            # Calculate progress
            total_questions = len(questions)
            completed_questions = sum(1 for q in questions if q.get("completed", False))
            
            if total_questions == 0:
                return 0.0
            
            progress = (completed_questions / total_questions) * 100
            
            # Record metrics
            self.metrics.record(
                "session_progress",
                progress,
                {"session_id": str(session_id)}
            )
            
            return progress
            
        except Exception as e:
            self.logger.error(f"Failed to calculate session progress: {str(e)}")
            return 0.0
    
    async def calculate_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Calculate user progress metrics.
        
        Args:
            user_id: User ID
            
        Returns:
            Progress metrics
        """
        try:
            # Get user sessions
            sessions = await self.session_service.get_user_sessions(user_id)
            if not sessions:
                return {
                    "total_sessions": 0,
                    "completed_sessions": 0,
                    "progress_percentage": 0.0,
                    "average_score": 0.0
                }
            
            # Calculate metrics
            total_sessions = len(sessions)
            completed_sessions = sum(1 for s in sessions if s.get("status") == "completed")
            total_score = sum(s.get("score", 0.0) for s in sessions if s.get("status") == "completed")
            
            progress = (completed_sessions / total_sessions) * 100 if total_sessions > 0 else 0.0
            average_score = total_score / completed_sessions if completed_sessions > 0 else 0.0
            
            # Create analysis result
            analysis = AnalysisResult(
                id=uuid4(),
                session_id=UUID(user_id),  # Using user_id as session_id for user-level analysis
                type=AnalysisType.OVERALL,
                status=AnalysisStatus.COMPLETED,
                start_time=datetime.now(timezone.utc),
                end_time=datetime.now(timezone.utc),
                duration=0.0,
                overall_score=average_score,
                metrics=[
                    {
                        "name": "session_completion",
                        "score": progress,
                        "weight": 1.0,
                        "feedback": f"User completed {completed_sessions}/{total_sessions} sessions",
                        "details": {
                            "total_sessions": total_sessions,
                            "completed_sessions": completed_sessions
                        }
                    },
                    {
                        "name": "question_completion",
                        "score": 0.0,  # TODO: Calculate question completion
                        "weight": 1.0,
                        "feedback": "Question completion metrics not yet implemented",
                        "details": {}
                    }
                ],
                summary=f"User completed {completed_sessions}/{total_sessions} sessions with average score {average_score:.2f}",
                recommendations=[],
                metadata={
                    "total_sessions": total_sessions,
                    "completed_sessions": completed_sessions,
                    "average_score": average_score
                }
            )
            
            # Store analysis
            await self.analysis_repository.store_analysis(analysis)
            
            # Record metrics
            self.metrics.record(
                "user_progress",
                progress,
                {"user_id": user_id}
            )
            self.metrics.record(
                "user_average_score",
                average_score,
                {"user_id": user_id}
            )
            
            return {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "progress_percentage": progress,
                "average_score": average_score
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate user progress: {str(e)}")
            return {
                "total_sessions": 0,
                "completed_sessions": 0,
                "progress_percentage": 0.0,
                "average_score": 0.0
            }
    
    async def get_admin_overview(self) -> Dict[str, Any]:
        """Get administrative overview.
        
        Returns:
            Administrative overview data
        """
        try:
            # Try to get from cache
            cache_key = "admin_overview"
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                self.metrics.record(
                    "analysis_cached_stats",
                    1,
                    {"type": "admin_overview"}
                )
                return cached_data
            
            # Get all sessions
            sessions = await self.session_service.get_all_sessions()
            
            # Calculate statistics
            total_sessions = len(sessions)
            active_sessions = sum(1 for s in sessions if s.get("status") == "active")
            completed_sessions = sum(1 for s in sessions if s.get("status") == "completed")
            total_users = len(set(s.get("user_id") for s in sessions))
            
            # Create overview
            overview = {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "completed_sessions": completed_sessions,
                "total_users": total_users,
                "completion_rate": (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0.0,
                "average_session_duration": 0.0,  # TODO: Calculate average duration
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Cache overview
            await self.cache.set(cache_key, overview, self.cache_ttl)
            
            # Record metrics
            self.metrics.record(
                "admin_overview_total_sessions",
                total_sessions,
                {"type": "total"}
            )
            self.metrics.record(
                "admin_overview_active_sessions",
                active_sessions,
                {"type": "active"}
            )
            self.metrics.record(
                "admin_overview_completed_sessions",
                completed_sessions,
                {"type": "completed"}
            )
            self.metrics.record(
                "admin_overview_total_users",
                total_users,
                {"type": "total"}
            )
            
            return overview
            
        except Exception as e:
            self.logger.error(f"Failed to get admin overview: {str(e)}")
            return {
                "total_sessions": 0,
                "active_sessions": 0,
                "completed_sessions": 0,
                "total_users": 0,
                "completion_rate": 0.0,
                "average_session_duration": 0.0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def get_job_statistics(self, job_id: str) -> Dict[str, Any]:
        """Get job statistics.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job statistics
        """
        try:
            # Try to get from cache
            cache_key = f"job_stats_{job_id}"
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                self.metrics.record(
                    "analysis_cached_stats",
                    1,
                    {"type": "job_statistics"}
                )
                return cached_data
            
            # Get job sessions
            sessions = await self.session_service.get_job_sessions(job_id)
            if not sessions:
                return {
                    "total_sessions": 0,
                    "completed_sessions": 0,
                    "completion_rate": 0.0,
                    "average_duration": 0.0,
                    "average_score": 0.0,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Calculate statistics
            total_sessions = len(sessions)
            completed_sessions = sum(1 for s in sessions if s.get("status") == "completed")
            total_duration = sum(s.get("duration", 0.0) for s in sessions if s.get("status") == "completed")
            total_score = sum(s.get("score", 0.0) for s in sessions if s.get("status") == "completed")
            
            completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0.0
            average_duration = total_duration / completed_sessions if completed_sessions > 0 else 0.0
            average_score = total_score / completed_sessions if completed_sessions > 0 else 0.0
            
            # Create statistics
            stats = {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "completion_rate": completion_rate,
                "average_duration": average_duration,
                "average_score": average_score,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Cache statistics
            await self.cache.set(cache_key, stats, self.cache_ttl)
            
            # Record metrics
            self.metrics.record(
                "job_completion_rate",
                completion_rate,
                {"job_id": job_id}
            )
            self.metrics.record(
                "job_average_duration",
                average_duration,
                {"job_id": job_id}
            )
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get job statistics: {str(e)}")
            return {
                "total_sessions": 0,
                "completed_sessions": 0,
                "completion_rate": 0.0,
                "average_duration": 0.0,
                "average_score": 0.0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    async def create_analysis(self, session_id: UUID, type: AnalysisType) -> AnalysisResult:
        """Create new analysis.
        
        Args:
            session_id: Session ID
            type: Analysis type
            
        Returns:
            Created analysis result
            
        Raises:
            AnalysisError: If creation fails
        """
        try:
            # Create analysis result
            analysis = AnalysisResult(
                id=uuid4(),
                session_id=session_id,
                type=type,
                status=AnalysisStatus.PENDING,
                start_time=datetime.now(timezone.utc)
            )
            
            # Store analysis
            await self.analysis_repository.store_analysis(analysis)
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    name="analysis_creation",
                    value=1.0,
                    labels={
                        "analysis_id": str(analysis.id),
                        "type": type.value
                    }
                )
            
            return analysis
        except Exception as e:
            raise AnalysisError(f"Failed to create analysis: {str(e)}")
    
    async def get_analysis(self, analysis_id: UUID) -> Optional[AnalysisResult]:
        """Get analysis result.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Analysis result if found, None otherwise
            
        Raises:
            AnalysisError: If retrieval fails
        """
        try:
            return await self.analysis_repository.get_analysis(analysis_id)
        except Exception as e:
            raise AnalysisError(f"Failed to get analysis: {str(e)}")
    
    async def create_session_analysis(
        self,
        session_id: UUID,
        user_id: UUID,
        job_id: UUID,
        total_questions: int
    ) -> AnalysisDTO:
        """Create new session analysis.
        
        Args:
            session_id: Session ID
            user_id: User ID
            job_id: Job ID
            total_questions: Total number of questions
            
        Returns:
            Created session analysis
            
        Raises:
            AnalysisError: If creation fails
        """
        try:
            # Create session analysis
            analysis = AnalysisDTO(
                id=uuid4(),
                session_id=session_id,
                user_id=user_id,
                job_id=job_id,
                start_time=datetime.now(timezone.utc),
                status=AnalysisStatus.PENDING,
                total_questions=total_questions,
                completed_questions=0,
                progress_percentage=0.0
            )
            
            # Store analysis
            await self.analysis_repository.store_session_analysis(analysis)
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    name="session_analysis_creation",
                    value=1.0,
                    labels={
                        "session_id": str(session_id),
                        "user_id": str(user_id),
                        "job_id": str(job_id)
                    }
                )
            
            return analysis
        except Exception as e:
            raise AnalysisError(f"Failed to create session analysis: {str(e)}")
    
    async def get_session_analysis(self, session_id: UUID) -> Optional[AnalysisDTO]:
        """Get session analysis.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session analysis if found, None otherwise
            
        Raises:
            AnalysisError: If retrieval fails
        """
        try:
            return await self.analysis_repository.get_session_analysis(session_id)
        except Exception as e:
            raise AnalysisError(f"Failed to get session analysis: {str(e)}")
    
    async def add_question_analysis(
        self,
        session_id: UUID,
        question_id: str,
        category: str,
        score: Optional[float] = None,
        feedback: Optional[str] = None,
        duration: Optional[float] = None
    ) -> AnalysisMetric:
        """Add question analysis to session.
        
        Args:
            session_id: Session ID
            question_id: Question ID
            category: Question category
            score: Question score
            feedback: Question feedback
            duration: Analysis duration
            
        Returns:
            Created question analysis
            
        Raises:
            AnalysisError: If addition fails
        """
        try:
            # Get session analysis
            session = await self.get_session_analysis(session_id)
            if not session:
                raise AnalysisError(f"Session analysis not found: {session_id}")
            
            # Create question analysis
            analysis = AnalysisMetric(
                id=uuid4(),
                question_id=question_id,
                category=category,
                status=QuestionStatus.COMPLETED,
                score=score,
                feedback=feedback,
                duration=duration
            )
            
            # Add to session
            session.add_question_analysis(analysis)
            
            # Store updated session
            await self.analysis_repository.store_session_analysis(session)
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    name="question_analysis_addition",
                    value=1.0,
                    labels={
                        "session_id": str(session_id),
                        "question_id": question_id,
                        "category": category
                    }
                )
            
            return analysis
        except Exception as e:
            raise AnalysisError(f"Failed to add question analysis: {str(e)}")
    
    async def complete_session_analysis(self, session_id: UUID) -> None:
        """Complete session analysis.
        
        Args:
            session_id: Session ID
            
        Raises:
            AnalysisError: If completion fails
        """
        try:
            # Get session analysis
            session = await self.get_session_analysis(session_id)
            if not session:
                raise AnalysisError(f"Session analysis not found: {session_id}")
            
            # Complete session
            session.complete()
            
            # Store updated session
            await self.analysis_repository.store_session_analysis(session)
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    name="session_analysis_completion",
                    value=1.0,
                    labels={"session_id": str(session_id)}
                )
        except Exception as e:
            raise AnalysisError(f"Failed to complete session analysis: {str(e)}")
    
    async def fail_session_analysis(self, session_id: UUID, error: str) -> None:
        """Mark session analysis as failed.
        
        Args:
            session_id: Session ID
            error: Error message
            
        Raises:
            AnalysisError: If failure marking fails
        """
        try:
            # Get session analysis
            session = await self.get_session_analysis(session_id)
            if not session:
                raise AnalysisError(f"Session analysis not found: {session_id}")
            
            # Mark as failed
            session.fail(error)
            
            # Store updated session
            await self.analysis_repository.store_session_analysis(session)
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    name="session_analysis_failure",
                    value=1.0,
                    labels={
                        "session_id": str(session_id),
                        "error": error
                    }
                )
        except Exception as e:
            raise AnalysisError(f"Failed to mark session analysis as failed: {str(e)}") 