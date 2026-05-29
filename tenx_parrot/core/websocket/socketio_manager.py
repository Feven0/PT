"""SocketIO manager implementation."""
from typing import Dict, Any, Optional, Callable, Awaitable, List, Union, Type, Set
import asyncio
from datetime import datetime, timezone
from time import perf_counter
import socketio
from pydantic import BaseModel

from core.logging import BackendLogger
from core.types.websocket import (
    SocketEvent,
    SocketEventData,
    MessageType,
    StateChangeEvent,
    Message
)
from core.types.components import HealthStatus, HealthStatusInfo, ComponentState
from core.base.lifecycle import LifecycleAware

# Define Message type union

logger = BackendLogger(__name__).get_logger()

class SocketIOManager(LifecycleAware):
    """SocketIO manager for handling real-time communication."""

    _instance: Optional['SocketIOManager'] = None
    _initialized: bool = False

    def __init__(
        self,
        cors_allowed_origins: Optional[List[str]] = ["*"],
        socketio_path: str = '/socket.io',
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize manager.
        
        Args:
            cors_allowed_origins: CORS allowed origins
            socketio_path: Socket.IO path
        """
        self._dependencies = dependencies or set()
        self.cors_allowed_origins = cors_allowed_origins
        self.socketio_path = socketio_path
        self._state = ComponentState.CREATED
        
        # Initialize required attributes
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._service_handlers: Dict[str, Dict[str, Callable]] = {}
        self.sio = None

        self._health_status = HealthStatusInfo(
            status=HealthStatus.UNKNOWN,
            details={
                "status": "initializing",
                "component": "socketio_manager",
                "initialized": False,
                "active_connections": 0,
                "registered_handlers": 0,
                "registered_services": 0
            }
        )
        
    @property
    def server(self) -> socketio.AsyncServer:
        """Get SocketIO server instance."""
        return self.sio

    async def initialize(self) -> None:
        """Initialize SocketIOManager."""
        logger.info("initializing socketio manager",
                    context="socketio_manager"
                    )
        
        try:
            if not SocketIOManager._instance:
                logger.info("creating socketio server",
                            context="socketio_manager"
                            )
                self.sio = socketio.AsyncServer(
                    async_mode='asgi',
                    cors_allowed_origins=self.cors_allowed_origins,
                    logger=True,
                    engineio_logger=True
                )
                
                # Set this instance as the singleton
                SocketIOManager._instance = self
                
            else:
                # Reuse existing instance
                self.sio = SocketIOManager._instance.sio
                self._event_handlers = SocketIOManager._instance._event_handlers
                self._sessions = SocketIOManager._instance._sessions
                self._service_handlers = SocketIOManager._instance._service_handlers
                self.socketio_path = SocketIOManager._instance.socketio_path
                self.health_status = SocketIOManager._instance.health_status
            
            # Setup default handlers
            self._setup_default_handlers()
            
            # Mark as initialized
            SocketIOManager._initialized = True
            
            # Update health status
            self.health_status.update(
                status=HealthStatus.HEALTHY,
                details={
                    "status": "initialized",
                    "initialized": True,
                    "active_connections": len(self._sessions),
                    "registered_handlers": len(self._event_handlers),
                    "registered_services": len(self._service_handlers),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            
            logger.info("socketio manager initialized successfully",
                        context="socketio_manager"
                        )
                        
        except Exception as e:
            logger.error(f"Failed to initialize socketio manager: {str(e)}",
                        context="socketio_manager",
                        error=str(e)
                        )
            self.health_status.update(
                status=HealthStatus.UNHEALTHY,
                details={
                    "error": str(e),
                    "message": "Failed to initialize",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            raise

    async def start(self) -> None:
        """Start SocketIOManager."""
        if not self.sio:
            logger.error("socketio manager not initialized",
                        context="socketio_manager"
                        )
            return
        
        logger.info("starting socketio manager",
                    context="socketio_manager"
                    )
            
    
    async def stop(self) -> None:
        """Stop the Socket.IO manager gracefully.
        
        This method:
        1. Closes all active sessions
        2. Unregisters all event handlers
        3. Unregisters all service handlers
        4. Disconnects all clients
        5. Updates health status
        """
        try:
            start_time = perf_counter()

            # Update health status to stopping
            self.health_status.update(
                status=HealthStatus.STOPPING,
                details={
                    "message": "Gracefully stopping SocketIO manager",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )


            if self.sio:
                # Close all active session
                if hasattr(self.sio.manager, 'rooms'):
                    for room in list(self.sio.manager.rooms.keys()):
                        try:
                            for sid in list(self.sio.manager.rooms[room]):
                                await self.close_session(sid)
                        except Exception as e:
                            logger.warning(f"Error closing session {room}: {str(e)}")

                # Unregister all event handlers
                if hasattr(self.sio, 'handlers'):
                    for event in list(self.sio.handlers.keys()):
                        try:
                            self.sio.handlers.pop(event, None)
                        except Exception as e:
                            logger.warning(f"Error unregistering handler for {event}: {str(e)}")

                # Unregister all service handlers
                for service_name in list(self._service_handlers.keys()):
                    try:
                        self._service_handlers.pop(service_name, None)
                    except Exception as e:
                        logger.warning(f"Error unregistering service {service_name}: {str(e)}")

                # Disconnect all clients
                if hasattr(self.sio.manager, 'clients'):
                    for sid in list(self.sio.manager.clients.keys()):
                        try:
                            await self.sio.disconnect(sid)
                        except Exception as e:
                            logger.warning(f"Error disconnecting client {sid}: {str(e)}")


            # Reset instance
            SocketIOManager._instance = None
            SocketIOManager._initialized = False
            self.sio = None
            self._event_handlers = {}
            self._sessions = {}
            self._service_handlers = {}

            # Update health status to stopped
            self.health_status.update(
                status=HealthStatus.STOPPED,
                details={
                    "message": "SocketIO manager stopped",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "duration": perf_counter() - start_time
                }
            )

            logger.info(
                "socketio_manager_stopped",
                duration=perf_counter() - start_time,
                context="socketio_manager"
            )

        except Exception as e:
            # Update health status to error
            self.health_status.update(
                status=HealthStatus.UNHEALTHY,
                details={
                    "error": str(e),
                    "message": "Error stopping SocketIO manager",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            raise
    
    async def check_health(self) -> HealthStatusInfo:
        """Check component health."""
        try:
            # Update health details
            self.health_status.update(details={
                "active_connections": len(self._sessions),
                "registered_handlers": sum(len(handlers) for handlers in self._event_handlers.values()),
                "registered_services": len(self._service_handlers),
                "last_checked": datetime.now(timezone.utc).isoformat()
            })
            
            # Check if server is running
            if self.sio and SocketIOManager._initialized:
                self.health_status.status = HealthStatus.HEALTHY
            else:
                self.health_status.status = HealthStatus.UNHEALTHY
                self.health_status.details["error"] = "Server not initialized"
                
        except Exception as e:
            self.health_status.status = HealthStatus.UNHEALTHY
            self.health_status.details["error"] = str(e)
            
        return self.health_status 
    

    @property
    def dependencies(self) -> Set[str]:
        """Get component dependencies."""
        return self._dependencies.copy()

    def add_dependency(self, component_name: str) -> None:
        """Add dependency.
        
        Args:
            component_name: Name of component to depend on
        """
        self._dependencies.add(component_name)
        
    def remove_dependency(self, component_name: str) -> None:
        """Remove dependency.
        
        Args:
            component_name: Name of component to remove dependency on
        """
        self._dependencies.discard(component_name)    


    @classmethod
    def get_instance(
        cls,
        cors_allowed_origins: Optional[List[str]] = ["*"],
        socketio_path: str = '/socket.io'
    ) -> 'SocketIOManager':
        """Get SocketIOManager instance."""
        if not cls._instance:
            cls._instance = cls(cors_allowed_origins, socketio_path)
        return cls._instance

    def create_asgi_app(self, fastapi_app: Any) -> Any:
        """Create ASGI application with FastAPI integration."""
        if not self.sio:
            logger.error("SocketIOManager is not initialized")
            return None
            
        return socketio.ASGIApp(
            socketio_server=self.sio,
            other_asgi_app=fastapi_app,
            socketio_path=self.socketio_path
        )

    def register_service_handlers(
        self,
        service_name: str,
        handlers: Dict[str, Callable]
    ) -> None:
        """Register service-specific event handlers."""
        self._service_handlers[service_name] = handlers
        for event, handler in handlers.items():
            self.register_handler(event, handler)

    def register_handler(
        self,
        event: SocketEvent,
        handler: Callable[[SocketEventData], Awaitable[None]],
        skip_sid: Optional[str] = None
    ) -> None:
        """Register event handler.
        
        Args:
            event: Event to handle
            handler: Handler function
            skip_sid: Optional session ID to skip
        """
        if not self._event_handlers:
            self._event_handlers = {}
            
        event_name = event.value if isinstance(event, SocketEvent) else event
        
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
            
        if handler not in self._event_handlers[event_name]:
            self._event_handlers[event_name].append(handler)
            
            # Update health status
            if hasattr(self, '_health_status'):
                self._health_status.details["registered_handlers"] = sum(
                    len(handlers) for handlers in self._event_handlers.values()
                )

    async def emit(
        self,
        event: SocketEvent,
        data: Dict[str, Any],
        room: Optional[str] = None,
        skip_sid: Optional[str] = None
    ) -> None:
        """Emit event to connected clients."""
        try:
            if room:
                await self.sio.emit(event, data, room=room, skip_sid=skip_sid)
            else:
                await self.sio.emit(event, data, skip_sid=skip_sid)
        except Exception as e:
            logger.error(f"Error emitting event {event}: {str(e)}")

    def _setup_default_handlers(self) -> None:
        """Setup default event handlers."""
        @self.sio.event
        async def connect(sid: str, environ: Dict[str, Any]):
            """Handle client connection."""
            logger.info(f"Client connected: {sid}")
            
            # Extract session info
            session_id = environ.get('HTTP_X_SESSION_ID')
            user_id = environ.get('HTTP_X_USER_ID')
            session_type = environ.get('HTTP_X_SESSION_TYPE', 'chat')
            
            if not session_id or not user_id:
                await self.sio.disconnect(sid)
                return
                
            # Join session room
            await self.sio.enter_room(sid, session_id)
            
            # Store session info
            self._sessions[sid] = {
                "user_id": user_id,
                "session_id": session_id,
                "session_type": session_type,
                "connected_at": datetime.now(timezone.utc)
            }
            
            # Emit connection event
            await self._handle_event(
                SocketEvent.CONNECT,
                {
                    "sid": sid,
                    "session_id": session_id,
                    "user_id": user_id,
                    "session_type": session_type
                }
            )

        @self.sio.event
        async def disconnect(sid: str):
            """Handle client disconnection."""
            logger.info(f"Client disconnected: {sid}")
            session = self._sessions.get(sid)
            if session:
                await self._handle_event(
                    SocketEvent.DISCONNECT,
                    {
                        "sid": sid,
                        "session_id": session["session_id"],
                        "user_id": session["user_id"]
                    }
                )
                del self._sessions[sid]

        # Chat events
        @self.sio.on(SocketEvent.CHAT_MESSAGE)
        async def handle_chat_message(sid: str, data: Dict[str, Any]):
            """Handle chat message."""
            session = self._sessions.get(sid)
            if session:
                await self._handle_event(
                    SocketEvent.CHAT_MESSAGE,
                    {
                        **data,
                        "session_id": session["session_id"],
                        "user_id": session["user_id"]
                    }
                )

        @self.sio.on(SocketEvent.CHAT_TYPING)
        async def handle_typing(sid: str, data: Dict[str, Any]):
            """Handle typing indicator."""
            session = self._sessions.get(sid)
            if session:
                await self._handle_event(
                    SocketEvent.CHAT_TYPING,
                    {
                        **data,
                        "session_id": session["session_id"],
                        "user_id": session["user_id"]
                    }
                )

        # Interview events
        @self.sio.on(SocketEvent.INTERVIEW_START)
        async def handle_interview_start(sid: str, data: Dict[str, Any]):
            """Handle interview start."""
            session = self._sessions.get(sid)
            if session:
                await self._handle_event(
                    SocketEvent.INTERVIEW_START,
                    {
                        **data,
                        "session_id": session["session_id"],
                        "user_id": session["user_id"]
                    }
                )

        @self.sio.on(SocketEvent.INTERVIEW_QUESTION)
        async def handle_interview_question(sid: str, data: Dict[str, Any]):
            """Handle interview question."""
            session = self._sessions.get(sid)
            if session:
                await self._handle_event(
                    SocketEvent.INTERVIEW_QUESTION,
                    {
                        **data,
                        "session_id": session["session_id"],
                        "user_id": session["user_id"]
                    }
                )

        @self.sio.on(SocketEvent.INTERVIEW_ANSWER)
        async def handle_interview_answer(sid: str, data: Dict[str, Any]):
            """Handle interview answer."""
            session = self._sessions.get(sid)
            if session:
                await self._handle_event(
                    SocketEvent.INTERVIEW_ANSWER,
                    {
                        **data,
                        "session_id": session["session_id"],
                        "user_id": session["user_id"]
                    }
                )

        # Audio events
        @self.sio.on(SocketEvent.WEBRTC_OFFER)
        async def handle_webrtc_offer(sid: str, data: Dict[str, Any]):
            """Handle WebRTC offer."""
            session = self._sessions.get(sid)
            if session:
                await self._handle_event(
                    SocketEvent.WEBRTC_OFFER,
                    {
                        **data,
                        "session_id": session["session_id"],
                        "user_id": session["user_id"]
                    }
                )

        @self.sio.on(SocketEvent.WEBRTC_ANSWER)
        async def handle_webrtc_answer(sid: str, data: Dict[str, Any]):
            """Handle WebRTC answer."""
            session = self._sessions.get(sid)
            if session:
                await self._handle_event(
                    SocketEvent.WEBRTC_ANSWER,
                    {
                        **data,
                        "session_id": session["session_id"],
                        "user_id": session["user_id"]
                    }
                )

        @self.sio.on(SocketEvent.WEBRTC_ICE)
        async def handle_webrtc_ice(sid: str, data: Dict[str, Any]):
            """Handle WebRTC ICE candidate."""
            session = self._sessions.get(sid)
            if session:
                await self._handle_event(
                    SocketEvent.WEBRTC_ICE,
                    {
                        **data,
                        "session_id": session["session_id"],
                        "user_id": session["user_id"]
                    }
                )

        # Audio transcription and chat
        @self.sio.on("audio transcribe")
        async def handle_audio_transcribe(sid: str, data: Dict[str, Any]):
            """Handle audio transcription."""
            session = self._sessions.get(sid)
            if session:
                await self._handle_event(
                    "audio.transcribe",
                    {
                        **data,
                        "session_id": session["session_id"],
                        "user_id": session["user_id"]
                    }
                )

        @self.sio.on("audio chat")
        async def handle_audio_chat(sid: str, data: Dict[str, Any]):
            """Handle audio chat."""
            session = self._sessions.get(sid)
            if session:
                await self._handle_event(
                    "audio.chat",
                    {
                        **data,
                        "session_id": session["session_id"],
                        "user_id": session["user_id"]
                    }
                )

    async def _handle_event(self, event: SocketEvent, data: Dict[str, Any]) -> None:
        """Handle socket event."""
        try:
            # Create event data model
            event_data = SocketEventData(
                event=event,
                data=data,
                room=data.get('session_id')
            )

            # Call registered handlers
            handlers = self._event_handlers.get(event, [])
            for handler in handlers:
                try:
                    await handler(event_data)
                except Exception as e:
                    logger.error(f"Event handler error: {str(e)}")
                    await self.emit(
                        SocketEvent.ERROR,
                        {
                            "error": str(e),
                            "event": event,
                            "handler": handler.__name__
                        },
                        room=data.get('session_id')
                    )

        except Exception as e:
            logger.error(f"Error handling event {event}: {str(e)}")
            await self.emit(
                SocketEvent.ERROR,
                {
                    "error": str(e),
                    "event": event
                }
            )

    async def broadcast_message(
        self,
        message: Message,
        room: Optional[str] = None
    ) -> None:
        """Broadcast message to connected clients.
        
        Args:
            message: Message to broadcast
            room: Optional room to broadcast to
        """
        try:
            event_data = {
                'message': message.dict(),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Determine event type based on message type
            event = {
                MessageType.TEXT: SocketEvent.CHAT_MESSAGE,
                MessageType.AUDIO: SocketEvent.AUDIO_CHAT,
                MessageType.STATE: SocketEvent.STATE_CHANGE,
                MessageType.NOTIFICATION: SocketEvent.NOTIFICATION,
                MessageType.ERROR: SocketEvent.ERROR
            }.get(message.type, SocketEvent.MESSAGE)
            
            if room:
                await self.sio.emit(event, event_data, room=room)
            else:
                await self.sio.emit(event, event_data)
                
        except Exception as e:
            logger.error(f"Error broadcasting message: {str(e)}")
            # Emit error event
            error_data = {
                'error': str(e),
                'message_type': message.type if message else None
            }
            if room:
                await self.sio.emit(SocketEvent.ERROR, error_data, room=room)
            else:
                await self.sio.emit(SocketEvent.ERROR, error_data)

    async def broadcast_state_change(
        self,
        state_change: StateChangeEvent,
        room: Optional[str] = None
    ) -> None:
        """Broadcast state change to connected clients."""
        try:
            event_data = state_change.dict()
            
            if room:
                await self.sio.emit(SocketEvent.STATE_CHANGE, event_data, room=room)
            else:
                await self.sio.emit(SocketEvent.STATE_CHANGE, event_data)
                
        except Exception as e:
            logger.error(f"Error broadcasting state change: {str(e)}")

    def get_session_data(self, sid: str) -> Optional[Dict[str, Any]]:
        """Get session data for client."""
        return self._sessions.get(sid)

    def update_session_data(self, sid: str, data: Dict[str, Any]) -> None:
        """Update session data for client."""
        if sid in self._sessions:
            self._sessions[sid].update(data)

    async def broadcast_to_service(
        self,
        service_name: str,
        event: str,
        data: Dict[str, Any],
        room: Optional[str] = None
    ) -> None:
        """Broadcast event to service clients."""
        try:
            if room:
                await self.sio.emit(f"{service_name}.{event}", data, room=room)
            else:
                await self.sio.emit(f"{service_name}.{event}", data)
        except Exception as e:
            logger.error(f"Error broadcasting to service {service_name}: {str(e)}")

    async def close_session(self, sid: str) -> None:
        """Close client session."""
        try:
            session = self._sessions.get(sid)
            if session:
                # Emit disconnect event
                await self._handle_event(
                    SocketEvent.DISCONNECT,
                    {
                        "sid": sid,
                        "session_id": session["session_id"],
                        "user_id": session["user_id"]
                    }
                )
                # Remove from rooms
                for room in await self.sio.get_rooms(sid):
                    await self.sio.leave_room(sid, room)
                # Remove session data
                del self._sessions[sid]
                # Disconnect socket
                await self.sio.disconnect(sid)
        except Exception as e:
            logger.error(f"Error closing session {sid}: {str(e)}")
