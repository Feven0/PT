"""Chat service implementation."""
from typing import Dict, List, Optional, Set, Union, Any
from datetime import datetime, timezone
import asyncio
import json
from uuid import UUID

from core.base.service import BaseService
from core.config.base import AppConfig
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.alert.manager import AlertManager
from core.types.components import HealthStatus, HealthStatusInfo
from core.telemetry.decorators import track_component_operation
from core.types.metrics import MetricType
from core.types.session import (
    SessionProgress,
    SessionState,
    SessionStateModel,
    SessionEvent,
    SessionType,
    SessionConfig
)
from core.types.websocket import (
    SocketEvent,
    SocketEventData,
    MessageType,
    MessageDirection,
    MessageStatus
)
from core.websocket.socketio_manager import SocketIOManager

from repositories.chat import ChatRepository
from services.session.service import SessionManagementService
from services.llm.chat.service import ChatLLMService  # Import the LLM service



class ChatError(Exception):
    """Base chat error."""
    pass

class ConfigError(ChatError):
    """Configuration error."""
    pass

class ChatService(BaseService):
    """Service for managing chat interactions."""
    
    REQUIRED_CONFIG = {
        "max_message_length": int,
        "max_history_size": int,
        "rate_limit": int,
        "timeout": int,
        "batch_size": int,
        "cache_ttl": int,
        "max_concurrent": int        
    }
    
    def __init__(
        self,
        name: str,
        config: AppConfig,
        session_service: SessionManagementService,
        chat_repository: ChatRepository,
        chat_llm_service: ChatLLMService,
        metrics: Optional[MetricsManager] = None,
        alert_manager: Optional[AlertManager] = None,
        socketio_manager: Optional[SocketIOManager] = None,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize chat service.
        
        Args:
            name: Service name
            config: Application configuration
            session_service: Session management service
            chat_repository: Chat repository for chat metadata
            chat_llm_service: Chat LLM service for AI interactions
            metrics: Optional metrics manager
            alert_manager: Optional alert manager
            socketio_manager: Optional SocketIO manager
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
        
        self.session_service = session_service
        self.chat_repository = chat_repository
        self.chat_llm_service = chat_llm_service
        self.alert_manager = alert_manager
        self.socketio_manager = socketio_manager or SocketIOManager.get_instance()
        
        # Get validated config
        config_dict = self._config
        
        # Initialize chat settings from validated config with defaults
        self._max_message_length = config_dict.get("max_message_length", 4096)  # 4KB default
        self._max_history_size = config_dict.get("max_history_size", 100)
        self._rate_limit = config_dict.get("rate_limit", 60)  # 60 messages per minute
        self._timeout = config_dict.get("timeout", 30)  # 30 seconds
        self._batch_size = config_dict.get("batch_size", 100)
        self._cache_ttl = config_dict.get("cache_ttl", 3600)
        self._max_concurrent = config_dict.get("max_concurrent", 10)
        
        # Initialize health status
        self._health_status = HealthStatusInfo(
            status=HealthStatus.STARTING,
            details={
                "status": "initializing",
                "component": self.name,
                "config": {
                    "max_message_length": self._max_message_length,
                    "max_history_size": self._max_history_size,
                    "rate_limit": self._rate_limit,
                    "timeout": self._timeout
                },
                "metrics": {
                    "active_sessions": 0,
                    "messages_processed": 0,
                    "errors": 0
                }
            }
        )
        
        # Register metrics if available
        if self.metrics:
            self._register_metrics()
            
        # Register socket event handlers
        self._register_handlers()
        
        self._active_chats: Dict[str, Dict] = {}
        self._message_history: List[Dict] = []
        self._sessions: Dict[str, SessionProgress] = {}
        self._lock = asyncio.Lock()
        self._connections: Dict[str, List[str]] = {}  # Added missing field
    
    def _register_metrics(self) -> None:
        """Register chat metrics."""
        # Operation metrics
        self.metrics.register_metric(
            f"{self.name}_operations_total",
            MetricType.COUNTER,
            f"Total number of operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Session metrics
        self.metrics.register_metric(
            f"{self.name}_active_sessions",
            MetricType.GAUGE,
            f"Number of active chat sessions in {self.name}"
        )
        
        self.metrics.register_metric(
            f"{self.name}_session_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of chat sessions in {self.name}"
        )
        
        # Message metrics
        self.metrics.register_metric(
            f"{self.name}_messages_total",
            MetricType.COUNTER,
            f"Total number of messages in {self.name}",
            labels={"type": "", "status": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_message_size_bytes",
            MetricType.HISTOGRAM,
            f"Size of messages in bytes in {self.name}",
            labels={"type": ""}
        )
        
        # Performance metrics
        self.metrics.register_metric(
            f"{self.name}_message_processing_duration_seconds",
            MetricType.HISTOGRAM,
            f"Time taken to process messages in {self.name}",
            labels={"type": ""}
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
            f"Total number of rate limit hits in {self.name}"
        )
        
        # Connection metrics
        self.metrics.register_metric(
            f"{self.name}_active_connections",
            MetricType.GAUGE,
            f"Number of active WebSocket connections in {self.name}"
        )

    def _register_handlers(self) -> None:
        """Register socket event handlers."""
        self.socketio_manager.register_handler(
            SocketEvent.CHAT_MESSAGE,
            self._handle_chat_message
        )
        self.socketio_manager.register_handler(
            SocketEvent.CHAT_TYPING,
            self._handle_typing
        )

    @track_component_operation("check_health")
    async def _check_health(self) -> Dict:
        """Check chat service health."""
        health_info = {
            "status": HealthStatus.UNKNOWN,
            "metrics": {
                "active_chats": len(self._active_chats),
                "total_messages": len(self._message_history),
                "active_sessions": len(self._sessions),
                "active_connections": sum(len(conns) for conns in self._connections.values())
            },
            "last_check": datetime.now()
        }
        
        try:
            # Check dependencies
            if self.session_service:
                await self.session_service.check_health()
                
            health_info["status"] = HealthStatus.HEALTHY
            
            # Update chat metrics
            self.update_chat_metrics()
            
            return health_info
            
        except Exception as e:
            self.logger.error(
                "chat_health_check_failed",
                context="error",
                error=str(e)
            )
            health_info["status"] = HealthStatus.UNHEALTHY
            health_info["error"] = str(e)
            return health_info
            
    async def _initialize_impl(self) -> None:
        """Initialize chat service."""
        return
        
    async def _start_impl(self) -> None:
        """Start chat service."""
        return
        
    async def _stop_impl(self) -> None:
        """Stop chat service."""
            
        # Cleanup local state
        chat_count = len(self._active_chats)
        message_count = len(self._message_history)
        self._active_chats.clear()
        self._message_history.clear()
        self._sessions.clear()
        
        # Record metrics
        if self.metrics:
            self.metrics.counter(
                "chat_cleanup_total",
                value=1,
                labels={
                    "chats_closed": chat_count,
                    "messages_cleared": message_count
                }
            )
    
    async def create_chat_session(
        self,
        user_id: str,
        title: str,
        chat_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new chat session.
        
        Args:
            user_id: User ID
            title: Chat title
            chat_type: Type of chat
            metadata: Optional metadata
            
        Returns:
            Created chat session
        """
        try:
            # Prepare metadata
            chat_metadata = metadata or {}
            chat_metadata["chat_type"] = chat_type
            
            # Create session through session service
            session = await self.session_service.create_session(
                user_id=user_id,
                session_type="chat",
                title=title,
                metadata=chat_metadata,
                config={
                    "max_message_length": self._max_message_length,
                    "max_history_size": self._max_history_size,
                    "rate_limit": self._rate_limit,
                    "timeout": self._timeout,
                    "batch_size": self._batch_size,
                    "cache_ttl": self._cache_ttl,
                    "max_concurrent": self._max_concurrent
                }
            )
            
            # Create chat metadata
            await self.chat_repository.create_chat_metadata(
                session_id=session.id,
                title=title,
                chat_type=chat_type,
                metadata=chat_metadata
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "create_chat_session", "status": "success"}
                )
                
                self.metrics.record(
                    f"{self.name}_chat_session_created",
                    1,
                    labels={"chat_type": chat_type}
                )
                
                self.metrics.record(
                    f"{self.name}_active_sessions",
                    1,
                    labels={"chat_type": chat_type}
                )
            
            # Emit session created event
            await self.socketio_manager.emit(
                SocketEvent.CHAT_SESSION_CREATED,
                {
                    "session_id": str(session.id),
                    "user_id": user_id,
                    "title": title,
                    "chat_type": chat_type,
                    "created_at": session.created_at.isoformat(),
                    "status": session.state.value
                },
                room=str(session.id)
            )
            
            return {
                "session_id": str(session.id),
                "user_id": user_id,
                "title": title,
                "chat_type": chat_type,
                "created_at": session.created_at.isoformat(),
                "status": session.state.value
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create chat session: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "create_chat_session", "status": "error"}
                )
                
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "create_chat_session"}
                )
            raise
    
    async def process_message(
        self,
        session_id: str,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a user message and generate a response.
        
        Args:
            session_id: Chat session ID
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
            response = await self.chat_llm_service.generate_chat_response(
                session_id=session_id,
                user_message=user_message,
                context=context
            )
            
            # Store assistant message
            await self.session_service.store_message(
                session_id=session_id,
                message={
                    "role": "assistant",
                    "content": response["text"],
                    "timestamp": datetime.now().isoformat(),
                    "metadata": response.get("metadata", {})
                }
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_message_processed",
                    1,
                    labels={"session_id": session_id}
                )
                
                # Record message size
                self.metrics.record(
                    f"{self.name}_message_size_bytes",
                    len(user_message.encode('utf-8')),
                    labels={"type": "user"}
                )
                
                self.metrics.record(
                    f"{self.name}_message_size_bytes",
                    len(response["text"].encode('utf-8')),
                    labels={"type": "assistant"}
                )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to process message: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "process_message"}
                )
            raise
            
    async def get_session(self, session_id: str) -> Optional[SessionProgress]:
        """Get chat session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Chat session if found, None otherwise
        """
        try:
            # Get session through session service
            session = await self.session_service.get_session(session_id)
            if not session:
                return None
                
            # Create chat session from session data
            chat_session = SessionProgress(
                id=session.id,
                created_at=session.created_at,
                messages=await self.session_service.get_messages(session_id)
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "get_session", "status": "success"}
                )
            
            return chat_session
                
        except Exception as e:
            self.logger.error(
                "chat_session_load_failed",
                error=str(e),
                session_id=session_id
            )
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "get_session"}
                )
            if self.alert_manager:
                await self.alert_manager.send_alert(
                    "chat_session_load_failed",
                    f"Failed to load chat session {session_id}: {str(e)}"
                )
            raise
            
    async def get_chat_messages(self, session_id: str, limit: Optional[int] = None, offset: Optional[int] = None):
        """Get messages for a chat session.
        
        This is a wrapper around session_service.get_session_messages for consistency.
        
        Args:
            session_id: Session ID
            limit: Optional page size
            offset: Optional offset
            
        Returns:
            List of chat messages
        """
        return await self.session_service.get_session_messages(session_id, limit, offset)
        
    async def send_message(
        self,
        session_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send chat message.
        
        Args:
            session_id: Session ID
            content: Message content
            metadata: Optional message metadata
        """
        try:
            # Create message
            message = TextMessage(
                content=content,
                direction=MessageDirection.OUTGOING,
                status=MessageStatus.SENT,
                metadata={
                    **(metadata or {}),
                    "session_id": session_id
                }
            )
            
            # Store message
            await self.session_service.store_message(session_id, message.dict())
            
            # Broadcast message
            await self.socketio_manager.broadcast_message(message, room=session_id)
            
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            raise
            
    async def _handle_chat_message(self, data: Dict[str, Any]) -> None:
        """Handle incoming chat message."""
        try:
            # Create message event
            message = SocketEventData(
                event=SocketEvent.CHAT_MESSAGE,
                data={
                    "content": data.get("content", ""),
                    "type": MessageType.TEXT,
                    "direction": MessageDirection.INBOUND,
                    "status": MessageStatus.PENDING,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "metadata": data.get("metadata", {})
                }
            )
            
            # Process message
            await self._process_message(message)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error handling chat message: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"type": "message_handling", "operation": "handle_chat_message"}
                )
            raise

    async def _handle_typing(self, data: Dict[str, Any]) -> None:
        """Handle typing indicator."""
        try:
            # Create typing event
            message = SocketEventData(
                event=SocketEvent.CHAT_TYPING,
                data={
                    "is_typing": data.get("is_typing", False),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "metadata": data.get("metadata", {})
                }
            )
            
            # Broadcast typing status
            await self._broadcast_typing(message)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error handling typing indicator: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"type": "typing_handling", "operation": "handle_typing"}
                )
            raise

    async def _process_message(self, message: SocketEventData) -> None:
        """Process a chat message.
        
        Args:
            message: Message to process
        """
        try:
            # Get message data
            data = message.data
            
            # Validate message
            if not data.get("content"):
                raise ValueError("Message content is required")
                
            # Get session
            session_id = data.get("session_id")
            if not session_id:
                raise ValueError("Session ID is required")
                
            session = await self.session_service.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
                
            # Update message status
            data["status"] = MessageStatus.DELIVERED
            
            # Process with LLM if needed
            if session.session_type == SessionType.CHAT:
                response = await self.chat_llm_service.process_message(
                    message=data["content"],
                    session_id=session_id
                )
                data["response"] = response
                
            # Broadcast message
            await self._broadcast_message(message)
            
            # Update metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_messages_total",
                    1,
                    labels={
                        "type": MessageType.TEXT,
                        "status": data["status"]
                    }
                )
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error processing message: {str(e)}")
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"type": "message_processing", "operation": "process_message"}
                )
            raise

    async def end_chat_session(self, session_id: str) -> Dict[str, Any]:
        """End a chat session."""
        # Update session state
        await self.session_service.update_session(
            session_id=session_id,
            updates={"state": "completed"}
        )
        
        # Get final session data
        session = await self.session_service.get_session(session_id)
        
        return {
            "session_id": session_id,
            "user_id": str(session.user_id),
            "ended_at": datetime.now().isoformat(),
            "status": "completed"
        } 