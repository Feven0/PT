"""Session event handlers."""
from typing import Dict, Any, Optional, Protocol
from datetime import datetime, timezone

from core.types.session import (
    SessionProgress,
    SessionState,
    SessionStateModel,
    SessionEvent,
    SessionType,
    SessionConfig
)
from core.types.websocket import (
    WebSocketEvent,
    StateChangeEvent,
    StateMessage,
    NotificationMessage
)


class SessionEventHandler(Protocol):
    """Session event handler protocol."""
    
    async def handle_state_change(
        self,
        session: SessionProgress,
        new_state: SessionState,
        reason: Optional[str] = None
    ) -> None:
        """Handle session state change."""
        ...

    async def handle_websocket_event(
        self,
        session: SessionProgress,
        event: WebSocketEvent
    ) -> None:
        """Handle WebSocket event."""
        ...

    async def handle_session_event(
        self,
        session: SessionProgress,
        event: SessionEvent
    ) -> None:
        """Handle session event."""
        ...


class DefaultSessionEventHandler:
    """Default implementation of session event handler."""

    def __init__(self, session_service: "SessionManagementService"):
        """Initialize handler.
        
        Args:
            session_service: Session management service
        """
        self._service = session_service

    async def handle_state_change(
        self,
        session: SessionProgress,
        new_state: SessionState,
        reason: Optional[str] = None
    ) -> None:
        """Handle session state change.
        
        Args:
            session: Session instance
            new_state: New session state
            reason: Optional reason for state change
        """
        # Create state change event
        event = StateChangeEvent(
            session_id=session.id,
            previous_state=session.state.dict(),
            new_state=new_state.dict(),
            change_reason=reason
        )

        # Update session state
        session.state = new_state
        session.updated_at = datetime.now(timezone.utc)

        # Create state message
        message = StateMessage(
            state_type="session",
            state_data=new_state.dict(),
            is_partial=False
        )

        # Broadcast state change
        await self._service.broadcast_message(session.id, message)

        # Notify observers
        await self._service.notify_observers(session.id, event)

    async def handle_websocket_event(
        self,
        session: SessionProgress,
        event: WebSocketEvent
    ) -> None:
        """Handle WebSocket event.
        
        Args:
            session: Session instance
            event: WebSocket event
        """
        # Update session activity
        session.state.last_activity = datetime.now(timezone.utc)

        # Handle different event types
        if event.type == "connect":
            session.state.websocket_state.connected = True
            session.state.websocket_state.client_id = event.client_id
            session.state.websocket_state.last_seen = event.timestamp
            
            # Notify connection
            message = NotificationMessage(
                title="WebSocket Connected",
                body=f"Session {session.id} connected",
                level="info"
            )
            await self._service.broadcast_message(session.id, message)

        elif event.type == "disconnect":
            session.state.websocket_state.connected = False
            session.state.websocket_state.last_seen = event.timestamp
            
            # Notify disconnection
            message = NotificationMessage(
                title="WebSocket Disconnected",
                body=f"Session {session.id} disconnected",
                level="warning"
            )
            await self._service.broadcast_message(session.id, message)

        # Update session
        await self._service.update_session(session)

    async def handle_session_event(
        self,
        session: SessionProgress,
        event: SessionEvent
    ) -> None:
        """Handle session event.
        
        Args:
            session: Session instance
            event: Session event
        """
        # Update session activity
        session.state.last_activity = datetime.now(timezone.utc)

        # Add event to session data
        if "events" not in session.data:
            session.data["events"] = []
        session.data["events"].append(event.dict())

        # Update metrics
        if "metrics" not in session.data:
            session.data["metrics"] = {"event_count": 0}
        session.data["metrics"]["event_count"] += 1

        # Update session
        await self._service.update_session(session)

        # Notify observers if needed
        if event.event_type in {"error", "warning", "critical"}:
            await self._service.notify_observers(session.id, event) 