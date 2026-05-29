"""Session repository implementation."""
from typing import Optional, List, Dict, Any, Set, Union
from datetime import datetime, timezone
from uuid import UUID
import time

from core.types.base import ComponentNames as CN
from core.base import BaseRepository
from core.config import AppConfig
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.alert.manager import AlertManager
from core.cache.manager import CacheManager
from core.resilience.rate_limiter import RateLimiter
from core.resilience.retry import RetryWithBackoff
from core.types.session import (
    SessionProgress,
    SessionState,
    SessionStateModel,
    SessionEvent,
    SessionType,
    SessionConfig
)
from core.types.metrics import MetricType
from infrastructure.strapi.client import StrapiClient
from infrastructure.strapi.services import StrapiServiceFactory
from infrastructure.strapi.schemas import IPersonaSession, IPersonaSessionSchema
from infrastructure.weaviate.client import WeaviateInfrastructureClient
from infrastructure.weaviate.dynamic import WeaviateDynamicService
from infrastructure.weaviate.schemas import get_schema


class SessionError(Exception):
    """Base session error."""
    pass

class ConfigError(SessionError):
    """Configuration error."""
    pass

class SessionNotFoundError(SessionError):
    """Error raised when session is not found."""
    pass

class SessionCreationError(SessionError):
    """Error raised when session creation fails."""
    pass

class SessionUpdateError(SessionError):
    """Error raised when session update fails."""
    pass

class SessionDeletionError(SessionError):
    """Error raised when session deletion fails."""
    pass

class SessionRepository(BaseRepository[SessionProgress]):
    """Session repository implementation."""

    REQUIRED_CONFIG = {
        'cache_ttl': int,
        'batch_size': int,
        'max_retries': int,
        'max_sessions': int,
        'session_timeout': int,
    }

    def __init__(
        self,
        name: str,
        config: AppConfig,     
        metrics: Optional[MetricsManager] = None,
        cache: Optional[CacheManager] = None,        
        strapi_client: Optional[StrapiClient] = None,
        weaviate_client: Optional[WeaviateInfrastructureClient] = None,
        alert_manager: Optional[AlertManager] = None,
        retry_manager: Optional[RetryWithBackoff] = None,
        rate_limiter: Optional[RateLimiter] = None,
        dependencies: Optional[Set[str]] = None,
    ):
        """Initialize session repository.
        
        Args:
            name: Repository name
            config: Application configuration
            metrics: Optional metrics manager
            cache: Optional cache manager
            logger: Optional logger instance
            dependencies: Optional set of dependency names
            strapi_client: Strapi client instance
            weaviate_client: Weaviate client instance
            alert_manager: Alert manager instance
        """
        # Initialize base repository
        required_deps = {CN.metrics_manager, 
                         CN.cache_manager, 
                         CN.strapi_client,
                         CN.weaviate_client,
                         CN.alert_manager}
        if dependencies:
            required_deps.update(dependencies)
            
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            cache=cache,
            dependencies=required_deps,
            required_config=self.REQUIRED_CONFIG
        )
              
        
        # Get validated repository config
        self._repository_config = self._config
        
        # Initialize session repository settings from validated config
        self._cache_ttl = self._repository_config.get('cache_ttl', 3600)
        self._batch_size = self._repository_config.get('batch_size', 100)
        self._max_retries = self._repository_config.get('max_retries', 3)
        self._max_sessions = self._repository_config.get('max_sessions', 10)
        self._session_timeout = self._repository_config.get('session_timeout', 3600)
        

        # Initialize components
        self._cache = cache
        self._alert_manager = alert_manager        
        self._rate_limiter = rate_limiter
        self._retry = retry_manager

        # Get Strapi service for sessions
        self._session_service = (StrapiServiceFactory(strapi_client, metrics)
                               .session_service)  
                
        # Initialize Weaviate service
        self.weaviate_client = weaviate_client
        self.weaviate_service = None
        if weaviate_client:
            self.weaviate_service = WeaviateDynamicService(
                client=weaviate_client,
                schema=get_schema("Analysis"),
                logger=self.logger
            )
        # Initialize resilience components
        if metrics:
            self._register_metrics()
            

        # Update health status with config details
        self.update_health_details({
            "config": {
                "cache_ttl": self._cache_ttl,
                "batch_size": self._batch_size,
                "max_retries": self._max_retries,
                "max_sessions": self._max_sessions,
                "session_timeout": self._session_timeout,
            }
        })
        
    def _register_metrics(self) -> None:
        """Register repository metrics."""
        if not self.metrics:
            return
            
        # Operation metrics
        self.metrics.register_metric(
            f"{self.name}_operations_total",
            MetricType.COUNTER,
            f"Total number of operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Performance metrics
        self.metrics.register_metric(
            f"{self.name}_operation_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of operations in {self.name}",
            labels={"operation": ""}
        )
        
        # Session metrics
        self.metrics.register_metric(
            f"{self.name}_active_sessions",
            MetricType.GAUGE,
            f"Number of active sessions in {self.name}",
            labels={"user_id": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_total_sessions",
            MetricType.COUNTER,
            f"Total number of sessions in {self.name}"
        )
        
        self.metrics.register_metric(
            f"{self.name}_session_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of sessions in {self.name}",
            labels={"type": "", "status": ""}
        )
        
        # Cache metrics
        self.metrics.register_metric(
            f"{self.name}_cache_hits_total",
            MetricType.COUNTER,
            f"Total number of cache hits in {self.name}",
            labels={"operation": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_cache_misses_total",
            MetricType.COUNTER,
            f"Total number of cache misses in {self.name}",
            labels={"operation": ""}
        )
        
        # Error metrics
        self.metrics.register_metric(
            f"{self.name}_errors_total",
            MetricType.COUNTER,
            f"Total number of errors in {self.name}",
            labels={"type": "", "operation": ""}
        )
        
        # Rate limit metrics
        self.metrics.register_metric(
            f"{self.name}_rate_limit_hits_total",
            MetricType.COUNTER,
            f"Total number of rate limit hits in {self.name}",
            labels={"operation": ""}
        )
        
        # Retry metrics
        self.metrics.register_metric(
            f"{self.name}_retries_total",
            MetricType.COUNTER,
            f"Total number of retries in {self.name}",
            labels={"operation": ""}
        )

    async def create_session(self, interview_id: UUID, user_id: UUID) -> SessionProgress:
        """Create a new session.
        
        Args:
            interview_id (UUID): Interview ID
            user_id (UUID): User ID
            
        Returns:
            SessionProgress: Created session data
            
        Raises:
            SessionCreationError: If session creation fails
            SessionError: If maximum number of active sessions is reached
        """
        operation = "create_session"
        start_time = time.time()
        
        try:
            # Validate input parameters
            if not interview_id:
                raise SessionCreationError("Interview ID is required")
            if not user_id:
                raise SessionCreationError("User ID is required")
                
            # Apply rate limiting
            async with self._rate_limiter.rate_limit(operation):
                # Create session with retry
                async with self._retry.retry_context(operation) as attempt:
                    # Check active sessions limit
                    active_sessions = await self.count_active_sessions(user_id)
                    if active_sessions >= self._max_sessions:
                        raise SessionError(f"Maximum number of active sessions ({self._max_sessions}) reached")
                    
                    # Create session in Strapi
                    session = IPersonaSession(
                        slug=str(interview_id),
                        status=SessionState.CREATED.value,
                        attributes={
                            "interview_id": str(interview_id),
                            "user_id": str(user_id),
                            "created_at": datetime.now(timezone.utc).isoformat(),
                            "updated_at": datetime.now(timezone.utc).isoformat(),
                            "config": {},
                            "metadata": {}
                        }
                    )
                    
                    created = await self._session_service.create(session)
                    
                    if not created:
                        raise SessionCreationError(f"Failed to create session for interview {interview_id} and user {user_id}")
                    
                    # Convert to SessionProgress
                    progress = SessionProgress(
                        id=created.id,
                        user_id=str(user_id),
                        session_type=SessionType.INTERACTIVE,
                        state=SessionStateModel(
                            status=SessionState(created.status),
                            last_activity=datetime.now(timezone.utc)
                        ),
                        created_at=datetime.fromisoformat(created.attributes["created_at"]),
                        updated_at=datetime.fromisoformat(created.attributes["updated_at"]),
                        config=SessionConfig(**created.attributes.get("config", {})),
                        data={}
                    )
                    
                    # Cache result
                    if self._cache:
                        cache_key = f"session:{progress.id}"
                        await self._cache.set(cache_key, progress.dict(), ttl=self._cache_ttl)
                    
                    # Record metrics
                    if self.metrics:
                        self.metrics.record(
                            f"{self.name}_create_success",
                            1,
                            labels={"operation": "create_session"}
                        )
                        self.metrics.record(
                            f"{self.name}_active_sessions",
                            1,
                            labels={"user_id": str(user_id)}
                        )
                        self.metrics.record(
                            f"{self.name}_total_sessions",
                            1
                        )
                    
                    return progress
                    
        except SessionCreationError:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": "creation_error", "operation": "create_session"}
                )
            raise
        except SessionError:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": "session_error", "operation": "create_session"}
                )
            raise
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "create_session"}
                )
            self.logger.error(
                "create_session_failed",
                context="session_repository",
                error=str(e)
            )
            if self._alert_manager:
                await self._alert_manager.alert(
                    "session_creation_failed",
                    f"Failed to create session: {str(e)}",
                    severity="error",
                    metadata={
                        "interview_id": str(interview_id),
                        "user_id": str(user_id),
                        "error": str(e)
                    }
                )
            raise SessionCreationError(f"Failed to create session: {str(e)}") from e

    async def get_session(self, id: str) -> SessionProgress:
        """Get session by ID.
        
        Args:
            id (str): Session ID string
            
        Returns:
            SessionProgress: Session data if found
            
        Raises:
            SessionNotFoundError: If session with the given ID is not found
            SessionError: If an error occurs during retrieval
        """
        operation = "get_session"
        start_time = time.time()
        
        try:
            # Apply rate limiting
            async with self._rate_limiter.rate_limit(operation):
                # Try cache first
                cache_key = f"session:{id}"
                if self._cache:
                    if cached := await self._cache.get(cache_key):
                        if self.metrics:
                            self.metrics.record(
                                f"{self.name}_cache_hits",
                                1
                            )
                        return SessionProgress(**cached)
                    if self.metrics:
                        self.metrics.record(
                            f"{self.name}_cache_misses",
                            1
                        )
                
                # Get from Strapi
                session = await self._session_service.find_one(id)
                if not session:
                    if self.metrics:
                        self.metrics.record(
                            f"{self.name}_not_found",
                            1,
                            labels={"session_id": str(id)}
                        )
                    raise SessionNotFoundError(f"Session with ID {id} not found")
                    
                # Convert to SessionProgress
                progress = SessionProgress(
                    id=session.id,
                    interview_id=UUID(session.attributes["interview_id"]),
                    user_id=UUID(session.attributes["user_id"]),
                    state=SessionState(session.status),
                    created_at=datetime.fromisoformat(session.attributes["created_at"]),
                    updated_at=datetime.fromisoformat(session.attributes["updated_at"]),
                    config=SessionConfig(**session.attributes.get("config", {})),
                    metadata=session.attributes.get("metadata", {})
                )
                
                # Cache result
                if self._cache:
                    await self._cache.set(cache_key, progress.dict(), ttl=self._cache_ttl)
                
                return progress
                
        except SessionNotFoundError:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_not_found",
                    1,
                    labels={"session_id": str(id)}
                )
            raise
        except Exception as e:
            self.logger.error(f"Failed to get session: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_get_error",
                    1,
                    labels={"error": str(e)}
                )
            if self._alert_manager:
                await self._alert_manager.alert(
                    "session_retrieval_failed",
                    f"Failed to get session: {str(e)}",
                    severity="error",
                    metadata={
                        "session_id": id,
                        "error": str(e)
                    }
                )
            raise SessionError(f"Failed to get session: {str(e)}") from e

    async def list_sessions(
        self,
        filter: Optional[Dict[str, Any]] = None,
        sort: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[SessionProgress]:
        """List sessions with optional filtering and pagination.
        
        Args:
            filter: Optional filter criteria
            sort: Optional sort criteria
            limit: Optional page size
            offset: Optional offset
            
        Returns:
            List of sessions
        """
        operation = "list_sessions"
        start_time = time.time()
        
        try:
            # Apply rate limiting
            async with self._rate_limiter.rate_limit(operation):
                # Build pagination
                pagination = {}
                if limit is not None:
                    pagination["pageSize"] = min(limit, self._batch_size)
                if offset is not None:
                    pagination["page"] = (offset // pagination.get("pageSize", self._batch_size)) + 1
                
                # Get from Strapi
                sessions = await self._session_service.find_many(
                    filters=filter,
                    sort=sort,
                    pagination=pagination
                )
                
                # Convert to SessionProgress
                progress_list = []
                for session in sessions:
                    progress = SessionProgress(
                        id=session.id,
                        interview_id=UUID(session.attributes["interview_id"]),
                        user_id=UUID(session.attributes["user_id"]),
                        state=SessionState(session.status),
                        created_at=datetime.fromisoformat(session.attributes["created_at"]),
                        updated_at=datetime.fromisoformat(session.attributes["updated_at"])
                    )
                    progress_list.append(progress)
                
                # Record metrics
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_{operation}",
                        1,
                        labels={"status": "success", "count": len(progress_list)}
                    )
                    self.metrics.record(
                        f"{self.name}_operation_duration_seconds",
                        time.time() - start_time,
                        labels={"operation": operation}
                    )
                
                return progress_list
                
        except Exception as e:
            self.logger.error(f"Failed to list sessions: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_list_error",
                    1,
                    labels={"error": str(e)}
                )
            if self._alert_manager:
                await self._alert_manager.alert(
                    "session_listing_failed",
                    f"Failed to list sessions: {str(e)}",
                    severity="error",
                    metadata={"error": str(e)}
                )
            raise

    async def update_session(self, id: str, session: SessionProgress) -> Optional[SessionProgress]:
        """Update existing session.
        
        Args:
            id: Session ID
            session: Updated session data
            
        Returns:
            Updated session if found, None otherwise
        """
        operation = "update_session"
        start_time = time.time()
        
        try:
            # Apply rate limiting
            async with self._rate_limiter.rate_limit(operation):
                # Convert to IPersonaSession
                strapi_session = IPersonaSession(
                    id=id,
                    slug=str(session.interview_id),
                    status=session.state.value,
                    attributes={
                        "interview_id": str(session.interview_id),
                        "user_id": str(session.user_id),
                        "created_at": session.created_at.isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                )
                
                # Update in Strapi
                updated = await self._session_service.update(id, strapi_session)
                if not updated:
                    return None
                    
                # Convert to SessionProgress
                progress = SessionProgress(
                    id=updated.id,
                    interview_id=UUID(updated.attributes["interview_id"]),
                    user_id=UUID(updated.attributes["user_id"]),
                    state=SessionState(updated.status),
                    created_at=datetime.fromisoformat(updated.attributes["created_at"]),
                    updated_at=datetime.fromisoformat(updated.attributes["updated_at"])
                )
                
                # Update cache
                if self._cache:
                    cache_key = f"session:{id}"
                    await self._cache.set(cache_key, progress.dict(), ttl=self._cache_ttl)
                
                # Record metrics
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_update_success",
                        1,
                        labels={"operation": "update_session"}
                    )
                    self.metrics.record(
                        f"{self.name}_active_sessions",
                        -1,
                        labels={"session_id": str(id)}
                    )
                
                return progress
                
        except Exception as e:
            self.logger.error(f"Failed to update session: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_update_error",
                    1,
                    labels={"error": str(e)}
                )
            if self._alert_manager:
                await self._alert_manager.alert(
                    "session_update_failed",
                    f"Failed to update session: {str(e)}",
                    severity="error",
                    metadata={
                        "session_id": id,
                        "error": str(e)
                    }
                )
            raise

    async def delete_session(self, id: str) -> bool:
        """Delete session.
        
        Args:
            id (str): Session ID string
            
        Returns:
            bool: True if session was deleted successfully
            
        Raises:
            SessionNotFoundError: If session with the given ID is not found
            SessionDeletionError: If session deletion fails
        """
        operation = "delete_session"
        start_time = time.time()
        
        try:
            # Validate input
            if not id:
                raise SessionDeletionError("Session ID is required")
                
            # Check if session exists
            session = await self.get_session(id)
            
            # Apply rate limiting
            async with self._rate_limiter.rate_limit(operation):
                # Delete from Strapi
                deleted = await self._session_service.delete(id)
                
                if not deleted:
                    raise SessionDeletionError(f"Failed to delete session with ID {id}")
                
                # Remove from cache
                if self._cache:
                    await self._cache.delete(f"session:{id}")
                    if self.metrics:
                        self.metrics.record(
                            f"{self.name}_active_sessions",
                            -1,
                            labels={"session_id": str(id)}
                        )
                
                return True
                
        except SessionNotFoundError:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_not_found",
                    1,
                    labels={"session_id": str(id)}
                )
            raise
        except Exception as e:
            self.logger.error(f"Failed to delete session: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_delete_error",
                    1,
                    labels={"error": str(e)}
                )
            if self._alert_manager:
                await self._alert_manager.alert(
                    "session_deletion_failed",
                    f"Failed to delete session: {str(e)}",
                    severity="error",
                    metadata={
                        "session_id": id,
                        "error": str(e)
                    }
                )
            raise SessionDeletionError(f"Failed to delete session: {str(e)}") from e

    async def count_active_sessions(self, user_id: Optional[UUID] = None) -> int:
        """Count active sessions.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            Number of active sessions
        """
        operation = "count_sessions"
        
        try:
            # Build filter
            filter = {"status": {"$ne": SessionState.CLOSED.value}}
            if user_id:
                filter["attributes.user_id"] = str(user_id)
            
            # Get count from Strapi
            count = await self._session_service.count(filters=filter)
            
            return count
            
        except Exception as e:
            self.logger.error(f"Failed to count active sessions: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_count_error",
                    1,
                    labels={"error": str(e)}
                )
            if self._alert_manager:
                await self._alert_manager.alert(
                    "session_count_failed",
                    f"Failed to count sessions: {str(e)}",
                    severity="error",
                    metadata={
                        "user_id": str(user_id) if user_id else None,
                        "error": str(e)
                    }
                )
            raise 

    async def store_analysis(
        self,
        session_id: str,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store session analysis."""
        try:
            # Create analysis data
            analysis_data = {
                "session_id": session_id,
                "content": analysis["content"],
                "metadata": analysis["metadata"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Store in Strapi
            stored = await self._session_service.create_analysis(analysis_data)
            
            # Store in vector DB for semantic search
            if self.weaviate_service:
                await self.weaviate_service.create({
                    "session_id": session_id,
                    "content": analysis["content"],
                    "metadata": analysis["metadata"],
                    "timestamp": analysis_data["created_at"]
                })
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_analysis_stored",
                    1,
                    labels={
                        "session_id": session_id,
                        "analysis_type": analysis["metadata"].get("analysis_type")
                    }
                )
            
            return stored
            
        except Exception as e:
            self.logger.error(f"Failed to store analysis: {str(e)}")
            raise RepositoryError(f"Failed to store analysis: {str(e)}") from e
            
    async def get_analyses(
        self,
        session_id: str,
        limit: Optional[int] = None,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get analyses for a session."""
        try:
            # Get from Strapi
            analyses = await self._session_service.list_analyses(
                session_id=session_id,
                limit=limit,
                offset=offset,
                filters=filters
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_analyses_retrieved",
                    len(analyses),
                    labels={
                        "session_id": session_id,
                        "count": len(analyses)
                    }
                )
            
            return analyses
            
        except Exception as e:
            self.logger.error(f"Failed to get analyses: {str(e)}")
            return []
            
    async def search_analyses(
        self,
        session_id: str,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search analyses using vector similarity."""
        try:
            if not self.weaviate_service:
                return []
                
            filters = {
                "session_id": session_id
            }
            
            # Search in vector DB
            results = await self.weaviate_service.search(
                query=query,
                filters=filters,
                limit=limit
            )
            
            # Get full analysis data from Strapi
            analyses = []
            for result in results:
                analysis = await self._session_service.get_analysis_by_content(
                    session_id=session_id,
                    content=result["content"]
                )
                if analysis:
                    analyses.append(analysis)
            
            return analyses
            
        except Exception as e:
            self.logger.error(f"Failed to search analyses: {str(e)}")
            return []
            
    async def delete_analyses(
        self,
        session_id: str
    ) -> bool:
        """Delete all analyses for a session."""
        try:
            # Delete from Strapi
            success = await self._session_service.delete_analyses(session_id)
            
            # Delete from vector DB
            if self.weaviate_service:
                filters = { 
                    "session_id": session_id
                }
                await self.weaviate_service.delete_by_filter(filters)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to delete analyses: {str(e)}")
            return False 

    async def get_user_sessions(
        self,
        user_id: UUID,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[SessionProgress]:
        """Get sessions for a specific user.
        
        Args:
            user_id: User ID to filter by
            limit: Optional page size
            offset: Optional offset
            
        Returns:
            List of user sessions
        """
        operation = "get_user_sessions"
        start_time = time.time()
        
        try:
            # Build filter for user ID
            filter = {
                "attributes.user_id": str(user_id)
            }
            
            # Use existing list_sessions method
            sessions = await self.list_sessions(
                filter=filter,
                sort=["created_at:desc"],
                limit=limit,
                offset=offset
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_{operation}",
                    1,
                    labels={"status": "success", "count": len(sessions)}
                )
                self.metrics.record(
                    f"{self.name}_operation_duration_seconds",
                    time.time() - start_time,
                    labels={"operation": operation}
                )
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"Failed to get user sessions: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_{operation}",
                    1,
                    labels={"status": "error", "error": str(e)}
                )
            if self._alert_manager:
                await self._alert_manager.alert(
                    "user_sessions_retrieval_failed",
                    f"Failed to get user sessions: {str(e)}",
                    severity="error",
                    metadata={
                        "user_id": str(user_id),
                        "error": str(e)
                    }
                )
            raise

    async def get_job_sessions(
        self,
        job_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[SessionProgress]:
        """Get sessions for a specific job.
        
        Args:
            job_id: Job ID to filter by
            limit: Optional page size
            offset: Optional offset
            
        Returns:
            List of job sessions
        """
        operation = "get_job_sessions"
        start_time = time.time()
        
        try:
            # Build filter for job ID
            filter = {
                "tinder_job_profile": {
                    "id": {"eq": job_id}
                }
            }
            
            # Use existing list_sessions method with Strapi filter format
            sessions = await self.list_sessions(
                filter=filter,
                sort=["created_at:desc"],
                limit=limit,
                offset=offset
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_{operation}",
                    1,
                    labels={"status": "success", "count": len(sessions)}
                )
                self.metrics.record(
                    f"{self.name}_operation_duration_seconds",
                    time.time() - start_time,
                    labels={"operation": operation}
                )
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"Failed to get job sessions: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_{operation}",
                    1,
                    labels={"status": "error", "error": str(e)}
                )
            if self._alert_manager:
                await self._alert_manager.alert(
                    "job_sessions_retrieval_failed",
                    f"Failed to get job sessions: {str(e)}",
                    severity="error",
                    metadata={
                        "job_id": job_id,
                        "error": str(e)
                    }
                )
            raise

    async def get_all_sessions(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[SessionProgress]:
        """Get all sessions with optional pagination.
        
        Args:
            limit: Optional page size
            offset: Optional offset
            
        Returns:
            List of all sessions
        """
        operation = "get_all_sessions"
        start_time = time.time()
        
        try:
            # Use existing list_sessions method without filters
            sessions = await self.list_sessions(
                sort=["created_at:desc"],
                limit=limit,
                offset=offset
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_{operation}",
                    1,
                    labels={"status": "success", "count": len(sessions)}
                )
                self.metrics.record(
                    f"{self.name}_operation_duration_seconds",
                    time.time() - start_time,
                    labels={"operation": operation}
                )
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"Failed to get all sessions: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_{operation}",
                    1,
                    labels={"status": "error", "error": str(e)}
                )
            if self._alert_manager:
                await self._alert_manager.alert(
                    "all_sessions_retrieval_failed",
                    f"Failed to get all sessions: {str(e)}",
                    severity="error",
                    metadata={"error": str(e)}
                )
            raise 

    async def get_session_messages(
        self,
        session_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get messages for a specific session.
        
        Args:
            session_id: Session ID
            limit: Optional page size
            offset: Optional offset
            
        Returns:
            List of session messages
        """
        try:
            self._metrics.increment(MetricType.REPOSITORY_OPERATION, labels={
                "repository": "session",
                "operation": "get_session_messages"
            })
            
            # Apply cache if available
            cache_key = f"session_messages_{session_id}_{limit}_{offset}"
            if self._cache:
                cached_result = await self._cache.get(cache_key)
                if cached_result:
                    return cached_result
            
            # Construct query parameters
            params = {
                "filters[session][id][$eq]": session_id
            }
            if limit is not None:
                params["pagination[limit]"] = limit
            if offset is not None:
                params["pagination[start]"] = offset
            
            # Execute query
            response = await self._storage_client.get_collection(
                collection="messages",
                params=params
            )
            
            # Process and return results
            messages = response.get("data", [])
            
            # Cache results if cache is available
            if self._cache:
                await self._cache.set(cache_key, messages, ttl=self._cache_ttl)
            
            return messages
            
        except Exception as e:
            self._metrics.increment(MetricType.REPOSITORY_ERROR, labels={
                "repository": "session",
                "operation": "get_session_messages",
                "error_type": type(e).__name__
            })
            self._logger.error(f"Failed to get session messages: {str(e)}")
            raise

    async def store_message(
        self,
        session_id: str,
        message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store a message for a session.
        
        Args:
            session_id: Session ID
            message: Message data
            
        Returns:
            Stored message
        """
        try:
            self._metrics.increment(MetricType.REPOSITORY_OPERATION, labels={
                "repository": "session",
                "operation": "store_message"
            })
            
            # Prepare message data
            message_data = {
                **message,
                "session": {"id": session_id}
            }
            
            # Execute create operation
            response = await self._storage_client.create_item(
                collection="messages",
                data=message_data
            )
            
            # Invalidate cache if available
            if self._cache:
                await self._cache.delete_pattern(f"session_messages_{session_id}_*")
            
            return response.get("data", {})
            
        except Exception as e:
            self._metrics.increment(MetricType.REPOSITORY_ERROR, labels={
                "repository": "session",
                "operation": "store_message",
                "error_type": type(e).__name__
            })
            self._logger.error(f"Failed to store message: {str(e)}")
            raise

    async def store_observation(
        self,
        session_id: str,
        observer_id: str,
        observation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store an observation for a session.
        
        Args:
            session_id: Session ID
            observer_id: Observer ID
            observation: Observation data
            
        Returns:
            Stored observation
        """
        try:
            self._metrics.increment(MetricType.REPOSITORY_OPERATION, labels={
                "repository": "session",
                "operation": "store_observation"
            })
            
            # Prepare observation data
            observation_data = {
                **observation,
                "session": {"id": session_id},
                "observer": {"id": observer_id}
            }
            
            # Execute create operation
            response = await self._storage_client.create_item(
                collection="observations",
                data=observation_data
            )
            
            # Invalidate cache if available
            if self._cache:
                await self._cache.delete_pattern(f"session_observations_{session_id}_*")
            
            return response.get("data", {})
            
        except Exception as e:
            self._metrics.increment(MetricType.REPOSITORY_ERROR, labels={
                "repository": "session",
                "operation": "store_observation",
                "error_type": type(e).__name__
            })
            self._logger.error(f"Failed to store observation: {str(e)}")
            raise

    async def get_session_observations(
        self,
        session_id: str,
        observer_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get observations for a session.
        
        Args:
            session_id: Session ID
            observer_id: Optional observer ID to filter by
            limit: Optional page size
            offset: Optional offset
            
        Returns:
            List of observations
        """
        try:
            self._metrics.increment(MetricType.REPOSITORY_OPERATION, labels={
                "repository": "session",
                "operation": "get_session_observations"
            })
            
            # Apply cache if available
            cache_key = f"session_observations_{session_id}_{observer_id}_{limit}_{offset}"
            if self._cache:
                cached_result = await self._cache.get(cache_key)
                if cached_result:
                    return cached_result
            
            # Construct query parameters
            params = {
                "filters[session][id][$eq]": session_id
            }
            if observer_id:
                params["filters[observer][id][$eq]"] = observer_id
            if limit is not None:
                params["pagination[limit]"] = limit
            if offset is not None:
                params["pagination[start]"] = offset
            
            # Execute query
            response = await self._storage_client.get_collection(
                collection="observations",
                params=params
            )
            
            # Process and return results
            observations = response.get("data", [])
            
            # Cache results if cache is available
            if self._cache:
                await self._cache.set(cache_key, observations, ttl=self._cache_ttl)
            
            return observations
            
        except Exception as e:
            self._metrics.increment(MetricType.REPOSITORY_ERROR, labels={
                "repository": "session",
                "operation": "get_session_observations",
                "error_type": type(e).__name__
            })
            self._logger.error(f"Failed to get session observations: {str(e)}")
            raise

    async def create_observer(
        self,
        session_id: str,
        observer_id: str,
        observer_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create an observer for a session.
        
        Args:
            session_id: Session ID
            observer_id: Observer ID
            observer_config: Observer configuration
            
        Returns:
            Created observer
        """
        try:
            self._metrics.increment(MetricType.REPOSITORY_OPERATION, labels={
                "repository": "session",
                "operation": "create_observer"
            })
            
            # Prepare observer data
            observer_data = {
                **observer_config,
                "session": {"id": session_id},
                "id": observer_id
            }
            
            # Execute create operation
            response = await self._storage_client.create_item(
                collection="observers",
                data=observer_data
            )
            
            return response.get("data", {})
            
        except Exception as e:
            self._metrics.increment(MetricType.REPOSITORY_ERROR, labels={
                "repository": "session",
                "operation": "create_observer",
                "error_type": type(e).__name__
            })
            self._logger.error(f"Failed to create observer: {str(e)}")
            raise

    async def store_summary(
        self,
        session_id: str,
        summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store a summary for a session.
        
        Args:
            session_id: Session ID
            summary: Summary data
            
        Returns:
            Stored summary
        """
        try:
            self._metrics.increment(MetricType.REPOSITORY_OPERATION, labels={
                "repository": "session",
                "operation": "store_summary"
            })
            
            # Prepare summary data
            summary_data = {
                **summary,
                "session": {"id": session_id}
            }
            
            # Execute create operation
            response = await self._storage_client.create_item(
                collection="summaries",
                data=summary_data
            )
            
            return response.get("data", {})
            
        except Exception as e:
            self._metrics.increment(MetricType.REPOSITORY_ERROR, labels={
                "repository": "session",
                "operation": "store_summary",
                "error_type": type(e).__name__
            })
            self._logger.error(f"Failed to store summary: {str(e)}")
            raise 