"""Session management implementation."""
from typing import Optional, Dict, Any, Set, List
from datetime import datetime, timezone
import asyncio
import uuid

from core.base.manager import BaseManager
from core.telemetry.metrics import MetricsManager
from core.logging import BackendLogger
from core.config import AppConfig
from core.types.metrics import MetricsProtocol, MetricType

from core.types.session import Session, SessionState


class SessionManager(BaseManager[Session]):
    """Session manager implementation."""
    
    def __init__(
        self,
        name: str,
        config: Any,
        logger: Optional[BackendLogger] = None,
        metrics: Optional[MetricsManager] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize session manager.
        
        Args:
            name: Session manager name
            config: Session manager configuration
            logger: Logger instance
            metrics: Metrics manager instance
            dependencies: Set of dependencies
        """
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies
        )
        
        self._sessions: Dict[str, Session] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._cleanup_interval = self._config.get("cleanup_interval_seconds", 60)
        
    async def _initialize_impl(self) -> None:
        """Initialize session manager."""
        self._sessions.clear()
        
        # Register metrics
        if self.metrics:
            self.metrics.register_metric(
                "active_sessions",
                MetricType.GAUGE,
                "Number of active sessions",
                labels={"name": self.name}
            )
            self.metrics.register_metric(
                "sessions_total",
                MetricType.COUNTER,
                "Total number of sessions",
                labels={"name": self.name, "state": ""}
            )
            self.metrics.register_metric(
                "sessions_expired_total",
                MetricType.COUNTER,
                "Total number of expired sessions",
                labels={"name": self.name}
            )
            
    async def _start_impl(self) -> None:
        """Start session manager."""
        # Start cleanup task
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
            
    async def _stop_impl(self) -> None:
        """Stop session manager."""
        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            
        # Clear sessions
        self._sessions.clear()
        
    async def _check_health_impl(self) -> None:
        """Check session manager health."""
        self._health_status.details.update({
            "active_sessions": len(self._sessions),
            "cleanup_task_running": bool(self._cleanup_task and not self._cleanup_task.done()),
            "session_states": {
                state.value: len([
                    s for s in self._sessions.values()
                    if s.state == state
                ])
                for state in SessionState
            }
        })
        
    async def create_session(
        self,
        user_id: str,
        session_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> Session:
        """Create new session.
        
        Args:
            user_id: User ID
            session_type: Session type
            metadata: Optional session metadata
            ttl: Optional time-to-live in seconds
            
        Returns:
            Created session
        """
        session = Session(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=session_type,
            metadata=metadata or {},
            ttl=ttl
        )
        
        self._sessions[session.id] = session
        
        if self.metrics:
            self.metrics.record(
                "sessions_total",
                1,
                labels={"name": self.name, "state": session.state.value}
            )
            self.metrics.record(
                "active_sessions",
                len(self._sessions),
                labels={"name": self.name}
            )
            
        await self.add_to_resource_pool("sessions", session)
        return session
        
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session if found
        """
        return self._sessions.get(session_id)
        
    async def get_user_sessions(
        self,
        user_id: str,
        session_type: Optional[str] = None
    ) -> List[Session]:
        """Get user sessions.
        
        Args:
            user_id: User ID
            session_type: Optional filter by type
            
        Returns:
            List of user sessions
        """
        sessions = [
            session for session in self._sessions.values()
            if session.user_id == user_id
        ]
        
        if session_type:
            sessions = [
                session for session in sessions
                if session.type == session_type
            ]
            
        return sessions
        
    async def update_session(
        self,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> Optional[Session]:
        """Update session.
        
        Args:
            session_id: Session ID
            metadata: Optional metadata to update
            ttl: Optional new TTL
            
        Returns:
            Updated session if found
        """
        session = self._sessions.get(session_id)
        if not session:
            return None
            
        if metadata:
            session.metadata.update(metadata)
            
        if ttl is not None:
            session.ttl = ttl
            session.updated_at = datetime.now(timezone.utc)
            
        return session
        
    async def close_session(self, session_id: str) -> Optional[Session]:
        """Close session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Closed session if found
        """
        session = self._sessions.get(session_id)
        if not session:
            return None
            
        session.state = SessionState.CLOSED
        session.closed_at = datetime.now(timezone.utc)
        
        await self.remove_from_resource_pool("sessions", session)
        return session
        
    async def _cleanup_expired_sessions(self) -> None:
        """Cleanup expired sessions."""
        while True:
            try:
                now = datetime.now(timezone.utc)
                expired_sessions = []
                
                # Find expired sessions
                for session in self._sessions.values():
                    if session.ttl and session.state == SessionState.ACTIVE:
                        age = (now - session.updated_at).total_seconds()
                        if age > session.ttl:
                            expired_sessions.append(session)
                            
                # Close expired sessions
                for session in expired_sessions:
                    await self.close_session(session.id)
                    
                    if self.metrics:
                        self.metrics.increment(
                            "sessions_expired_total",
                            labels={"name": self.name}
                        )
                        
                # Sleep before next cleanup
                await asyncio.sleep(self._cleanup_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(
                    "session_cleanup_failed",
                    error=str(e),
                    manager=self.name
                )
                await asyncio.sleep(60)  # Retry after 1 minute 