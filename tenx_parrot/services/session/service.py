"""Session management service."""
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timezone
from uuid import uuid4, UUID

from core.types.session import (
    SessionProgress,
    SessionState,
    SessionStateModel,
    SessionEvent,
    SessionType,
    SessionConfig
)
from core.types.websocket import (
    MessageType,
    SocketEvent,
    SocketEventData,
    StateChangeEvent
)
from core.base.service import BaseService
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.types.components import ComponentNames as CN
from core.config.base import AppConfig
from repositories.session import SessionRepository
from repositories.observer import ObserverRepository
from core.cache.manager import CacheManager
from core.errors.exceptions import ServiceError
from core.websocket.socketio_manager import SocketIOManager

logger = BackendLogger(__name__).get_logger()

class SessionStateError(ServiceError):
    """Session state error."""
    pass

class SessionManagementService(BaseService):
    """Session management service."""

    def __init__(
        self,
        name: str,
        config: AppConfig,
        session_repository: SessionRepository,
        observer_repository: ObserverRepository,
        metrics: Optional[MetricsManager] = None,
        cache: Optional[CacheManager] = None,
        socketio_manager: Optional[SocketIOManager] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize service."""
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies
        )

        self.session_repository = session_repository
        self.observer_repository = observer_repository
        self.cache = cache or CacheManager(
            name=CN.cache_manager,
            config=config
        )
        self.socketio_manager = socketio_manager or SocketIOManager.get_instance()
        
        # Register socket event handlers
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register socket event handlers."""
        self.socketio_manager.register_handler(
            SocketEvent.SESSION_STATE,
            self._handle_state_change
        )
        self.socketio_manager.register_handler(
            SocketEvent.SESSION_MESSAGE,
            self._handle_message
        )
        self.socketio_manager.register_handler(
            SocketEvent.CONNECT,
            self._handle_connect
        )
        self.socketio_manager.register_handler(
            SocketEvent.DISCONNECT,
            self._handle_disconnect
        )

    async def _validate_state_transition(
        self,
        session: SessionProgress,
        new_state: str
    ) -> bool:
        """Validate session state transition.
        
        Args:
            session: Current session
            new_state: New state to transition to
            
        Returns:
            True if transition is valid
            
        Raises:
            SessionStateError: If transition is invalid
        """
        valid_transitions = {
            SessionState.CREATED: [SessionState.ACTIVE, SessionState.ERROR],
            SessionState.ACTIVE: [SessionState.PAUSED, SessionState.COMPLETED, SessionState.ERROR],
            SessionState.PAUSED: [SessionState.ACTIVE, SessionState.COMPLETED, SessionState.ERROR],
            SessionState.COMPLETED: [SessionState.ERROR],
            SessionState.ERROR: [SessionState.ACTIVE]
        }
        
        if session.state not in valid_transitions:
            raise SessionStateError(f"Invalid current state: {session.state}")
            
        if new_state not in valid_transitions[session.state]:
            raise SessionStateError(
                f"Invalid state transition from {session.state} to {new_state}"
            )
            
        return True

    async def _handle_connect(self, event: SocketEventData) -> None:
        """Handle client connection event."""
        try:
            session_id = event.room
            if not session_id:
                raise ValueError("Session ID required")
                
            # Update session state
            session = await self.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
                
            await self._validate_state_transition(session, SessionState.ACTIVE)
            session.state = SessionState.ACTIVE
            session.metadata["last_connected"] = datetime.now(timezone.utc).isoformat()
            
            await self.session_repository.update_session(session)
            
            # Broadcast connection event
            await self.socketio_manager.emit(
                SocketEvent.SESSION_STATE,
                StateChangeEvent(
                    session_id=session_id,
                    previous_state={"state": session.state},
                    new_state={"state": SessionState.ACTIVE},
                    change_reason="client_connected"
                ).dict(),
                room=session_id
            )
            
        except Exception as e:
            self.logger.error(f"Error handling connection: {str(e)}")
            raise

    async def _handle_disconnect(self, event: SocketEventData) -> None:
        """Handle client disconnection event."""
        try:
            session_id = event.room
            if not session_id:
                raise ValueError("Session ID required")
                
            # Update session state
            session = await self.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
                
            await self._validate_state_transition(session, SessionState.PAUSED)
            session.state = SessionState.PAUSED
            session.metadata["last_disconnected"] = datetime.now(timezone.utc).isoformat()
            
            await self.session_repository.update_session(session)
            
            # Broadcast disconnection event
            await self.socketio_manager.emit(
                SocketEvent.SESSION_STATE,
                StateChangeEvent(
                    session_id=session_id,
                    previous_state={"state": session.state},
                    new_state={"state": SessionState.PAUSED},
                    change_reason="client_disconnected"
                ).dict(),
                room=session_id
            )
            
        except Exception as e:
            self.logger.error(f"Error handling disconnection: {str(e)}")
            raise

    async def _handle_state_change(self, event: SocketEventData) -> None:
        """Handle session state change event."""
        try:
            session_id = event.room
            if not session_id:
                raise ValueError("Session ID required")
                
            new_state = event.data.get("state")
            if not new_state:
                raise ValueError("New state required")
                
            # Update session state
            session = await self.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
                
            # Validate state transition
            await self._validate_state_transition(session, new_state)
            
            previous_state = session.state
            session.state = new_state
            session.updated_at = datetime.now(timezone.utc)
            
            await self.session_repository.update_session(session)
            
            # Broadcast state change
            await self.socketio_manager.emit(
                SocketEvent.SESSION_STATE,
                StateChangeEvent(
                    session_id=session_id,
                    previous_state={"state": previous_state},
                    new_state={"state": new_state},
                    change_reason=event.data.get("reason", "state_updated")
                ).dict(),
                room=session_id
            )
            
        except SessionStateError as e:
            self.logger.error(f"Invalid state transition: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error handling state change: {str(e)}")
            raise

    async def create_session(
        self,
        user_id: str,
        session_type: str = "general",
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SessionProgress:
        """Create a new session.
        
        Args:
            user_id: User ID
            session_type: Type of session (e.g., "chat", "interview")
            title: Optional session title
            metadata: Optional session metadata
            
        Returns:
            Created session
        """
        try:
            # Generate session ID
            session_id = str(uuid4())
            
            # Set default title if not provided
            if not title:
                title = f"Session {session_id[:8]} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Initialize metadata if not provided
            if metadata is None:
                metadata = {}
                
            # Add session type to metadata
            metadata["session_type"] = session_type
            
            # Create session
            session = await self.session_repository.create_session(
                session_id=session_id,
                user_id=user_id,
                session_type=SessionType(session_type),
                title=title,
                metadata=metadata
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "create_session", "status": "success"}
                )
                
                self.metrics.record(
                    f"{self.name}_sessions_created_total",
                    1,
                    labels={"session_type": session_type}
                )
            
            return session
            
        except Exception as e:
            self.logger.error(f"Failed to create session: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "create_session", "status": "error"}
                )
                
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "create_session"}
                )
            raise SessionStateError(f"Failed to create session: {str(e)}")

    async def get_session(self, session_id: str) -> Optional[SessionProgress]:
        """Get session by ID."""
        return await self.session_repository.get_session(session_id)

    async def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> Optional[SessionProgress]:
        """Update session."""
        session = await self.get_session(session_id)
        if not session:
            return None
            
        session.updated_at = datetime.now(timezone.utc)
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)
                
        return await self.session_repository.update_session(session_id, session)

    async def store_message(self, session_id: str, message: Dict[str, Any]) -> None:
        """Store session message."""
        await self.session_repository.store_message(session_id, message)
        
        # Broadcast message to session room
        await self.socketio_manager.emit(
            SocketEvent.SESSION_MESSAGE,
            message,
            room=session_id
        )

    async def get_user_sessions(
        self,
        user_id: str,
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
        try:
            return await self.session_repository.get_user_sessions(
                user_id=UUID(user_id) if isinstance(user_id, str) else user_id,
                limit=limit,
                offset=offset
            )
        except Exception as e:
            self.logger.error(f"Failed to get user sessions: {e}")
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
        try:
            return await self.session_repository.get_job_sessions(
                job_id=job_id,
                limit=limit,
                offset=offset
            )
        except Exception as e:
            self.logger.error(f"Failed to get job sessions: {e}")
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
        try:
            return await self.session_repository.get_all_sessions(
                limit=limit,
                offset=offset
            )
        except Exception as e:
            self.logger.error(f"Failed to get all sessions: {e}")
            raise

    async def _handle_message(self, event: SocketEventData) -> None:
        """Handle session message event."""
        try:
            session_id = event.room
            if not session_id:
                raise ValueError("Session ID required")
                
            message = event.data
            if not message:
                raise ValueError("Message data required")
                
            # Store message
            await self.store_message(session_id, message)
            
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            raise

    async def get_messages(
        self,
        session_id: str,
        limit: int = 50,
        message_type: Optional[MessageType] = None
    ) -> List[Dict[str, Any]]:
        """Get session message history."""
        key = f"messages:{session_id}"
        messages = await self.cache.get(key) or []
        
        if message_type:
            messages = [m for m in messages if m.get("type") == message_type]
            
        return messages[-limit:]

    async def get_session_metrics(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Get session metrics."""
        key = f"metrics:{session_id}"
        metrics = await self.cache.get(key) or {}
        
        # Calculate additional metrics
        if metrics.get("response_times"):
            metrics["avg_response_time"] = sum(metrics["response_times"]) / len(metrics["response_times"])
            
        return metrics

    async def add_observer(
        self,
        session_id: str,
        observer_id: str
    ) -> None:
        """Add observer to session."""
        await self.observer_repository.create_observer(
            session_id,
            {"observer_id": observer_id}
        )

    async def get_observers(
        self,
        session_id: str
    ) -> List[Dict[str, Any]]:
        """Get session observers."""
        observers = await self.observer_repository.list_observers(session_id)
        return [obs.dict() for obs in observers]

    async def notify_observers(
        self,
        session_id: str,
        event: Dict[str, Any]
    ) -> None:
        """Notify session observers of event."""
        observers = await self.get_observers(session_id)
        for observer in observers:
            await self.observer_repository.notify_observer(
                observer["id"],
                event
            )

    async def close_session(self, session_id: str) -> None:
        """Close session."""
        # Update session state
        await self.update_session(
            session_id,
            {"state": SessionState.CLOSED}
        )
        
        # Notify observers
        await self.notify_observers(
            session_id,
            {
                "type": "session_closed",
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

    async def analyze_session(
        self,
        session_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        analysis_type: str = "conversation"
    ) -> Dict[str, Any]:
        """Analyze a session."""
        try:
            # Get session
            session = await self.session_repository.get_session(session_id)
            if not session:
                raise ServiceError(f"Session {session_id} not found")
                
            # Get messages for analysis
            messages = await self.session_repository.get_messages(
                session_id=session_id,
                filters={
                    "created_at_gte": start_time.isoformat() if start_time else None,
                    "created_at_lte": end_time.isoformat() if end_time else None
                }
            )
            
            if not messages:
                raise ServiceError(f"No messages found for analysis in session {session_id}")
                
            # Process analysis based on type
            if analysis_type == "conversation":
                analysis = await self._analyze_conversation(messages)
            else:
                raise ServiceError(f"Unsupported analysis type: {analysis_type}")
                
            # Store analysis
            stored_analysis = await self.session_repository.store_analysis(
                session_id=session_id,
                analysis={
                    "content": analysis["content"],
                    "metadata": {
                        "analysis_type": analysis_type,
                        "message_count": len(messages),
                        "time_range": {
                            "start": start_time.isoformat() if start_time else None,
                            "end": end_time.isoformat() if end_time else None
                        },
                        "generated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            return stored_analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze session: {str(e)}")
            raise ServiceError(f"Failed to analyze session: {str(e)}") from e
            
    async def get_session_analyses(
        self,
        session_id: str,
        limit: Optional[int] = None,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get analyses for a session."""
        try:
            return await self.session_repository.get_analyses(
                session_id=session_id,
                limit=limit,
                offset=offset,
                filters=filters
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get session analyses: {str(e)}")
            return []
            
    async def search_analyses(
        self,
        session_id: str,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search session analyses."""
        try:
            return await self.session_repository.search_analyses(
                session_id=session_id,
                query=query,
                limit=limit
            )
            
        except Exception as e:
            self.logger.error(f"Failed to search analyses: {str(e)}")
            return []
            
    async def delete_session_analyses(
        self,
        session_id: str
    ) -> bool:
        """Delete all analyses for a session."""
        try:
            return await self.session_repository.delete_analyses(session_id)
            
        except Exception as e:
            self.logger.error(f"Failed to delete session analyses: {str(e)}")
            return False
            
    async def _analyze_conversation(
        self,
        messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze conversation messages."""
        try:
            # Prepare analysis prompt
            analysis_prompt = f"""
            Analyze the following conversation and provide:
            1. Key topics discussed
            2. Sentiment analysis
            3. Main questions/concerns
            4. Action items or next steps
            5. Overall engagement level
            
            Messages:
            {[f"{msg['role']}: {msg['content']}" for msg in messages]}
            """
            
            # Get analysis from LLM
            response = await self.llm_client.generate(
                messages=[
                    Message(role="system", content="You are an expert conversation analyzer."),
                    Message(role="user", content=analysis_prompt)
                ]
            )
            
            return {
                "content": response.content,
                "metadata": response.metadata
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze conversation: {str(e)}")
            raise ServiceError(f"Failed to analyze conversation: {str(e)}") from e

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
            return await self.session_repository.get_session_messages(
                session_id=session_id,
                limit=limit,
                offset=offset
            )
        except Exception as e:
            self.logger.error(f"Failed to get session messages: {e}")
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
            return await self.session_repository.store_observation(
                session_id=session_id,
                observer_id=observer_id,
                observation=observation
            )
        except Exception as e:
            self.logger.error(f"Failed to store observation: {e}")
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
            return await self.session_repository.get_session_observations(
                session_id=session_id,
                observer_id=observer_id,
                limit=limit,
                offset=offset
            )
        except Exception as e:
            self.logger.error(f"Failed to get session observations: {e}")
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
            return await self.session_repository.create_observer(
                session_id=session_id,
                observer_id=observer_id,
                observer_config=observer_config
            )
        except Exception as e:
            self.logger.error(f"Failed to create observer: {e}")
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
            return await self.session_repository.store_summary(
                session_id=session_id,
                summary=summary
            )
        except Exception as e:
            self.logger.error(f"Failed to store summary: {e}")
            raise 