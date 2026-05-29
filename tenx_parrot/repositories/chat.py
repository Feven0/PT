"""Chat repository implementation."""
from typing import Optional, List, Dict, Any, Set, Union
from datetime import datetime
from uuid import UUID

from core.types.base import ComponentNames as CN
from core.base import BaseRepository
from core.config import AppConfig
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.alert.manager import AlertManager
from core.cache.manager import CacheManager
from core.resilience.rate_limiter import RateLimiter
from core.resilience.retry import RetryWithBackoff
from core.types.chat import (
    ChatSession,
    ChatMessage,
    ChatState,
    ChatEvent,
    ChatType
)
from core.types.metrics import MetricType
from infrastructure.strapi.client import StrapiClient
from infrastructure.strapi.services import StrapiServiceFactory
from infrastructure.weaviate.client import WeaviateInfrastructureClient
from infrastructure.weaviate.dynamic import WeaviateDynamicService
from infrastructure.weaviate.schemas import get_schema

class ChatError(Exception):
    """Base chat error."""
    pass

class ConfigError(ChatError):
    """Configuration error."""
    pass

class ChatNotFoundError(ChatError):
    """Error raised when chat session is not found."""
    pass

class ChatCreationError(ChatError):
    """Error raised when chat session creation fails."""
    pass

class ChatUpdateError(ChatError):
    """Error raised when chat session update fails."""
    pass

class ChatDeletionError(ChatError):
    """Error raised when chat session deletion fails."""
    pass

class MessageNotFoundError(ChatError):
    """Error raised when chat message is not found."""
    pass

class MessageCreationError(ChatError):
    """Error raised when chat message creation fails."""
    pass

class ChatRepository(BaseRepository):
    """Repository for managing chat messages and metadata."""

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
        strapi_client: StrapiClient,
        weaviate_client: WeaviateInfrastructureClient,
        metrics: Optional[MetricsManager] = None,
        alerts: Optional[AlertManager] = None,
        cache: Optional[CacheManager] = None,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize chat repository."""
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies,
            required_config=self.REQUIRED_CONFIG
        )
        
        # Store clients
        self.strapi_client = strapi_client
        self.weaviate_client = weaviate_client

        # Initialize services
        self.strapi_service = StrapiServiceFactory(strapi_client, metrics).chat_service
        self.weaviate_service = WeaviateDynamicService(
            client=weaviate_client,
            schema=get_schema("ChatSession"),
            logger=logger
        )

        
        # Store config
        self.cache_ttl = self._config.get('cache_ttl', 3600)
        self.batch_size = self._config.get('batch_size', 100)
        self.max_retries = self._config.get('max_retries', 3)
        self.max_sessions = self._config.get('max_sessions', 1000)
        self.session_timeout = self._config.get('session_timeout', 3600)
        
        # Initialize utilities
        self.metrics = metrics
        self.alerts = alerts
        self.cache = cache
        self.logger = logger or BackendLogger(__name__)
        
        # Initialize state
        self._active_sessions: Dict[str, ChatSession] = {}
        self._session_events: Dict[str, List[ChatEvent]] = {}
        
    async def initialize(self) -> None:
        """Initialize repository."""
        await self.weaviate_service.initialize()
        
    async def create_chat_metadata(
        self,
        session_id: str,
        title: str,
        chat_type: ChatType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create chat metadata for an existing session.
        
        Args:
            session_id: ID of the existing session
            title: Chat title
            chat_type: Type of chat
            metadata: Optional additional metadata
            
        Returns:
            Created chat metadata
        """
        try:
            # Validate input
            if not session_id:
                raise ChatCreationError("Session ID is required")
            if not title:
                raise ChatCreationError("Title is required")
            if not chat_type:
                raise ChatCreationError("Chat type is required")
                
            # Create chat metadata in Strapi
            chat_data = {
                "session_id": session_id,
                "title": title,
                "type": chat_type.value,
                "metadata": metadata or {},
            }
            
            # chat_metadata = await self.strapi_service.create(chat_data)
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_chat_metadata_created",
                    1,
                    labels={
                        "session_id": session_id,
                        "chat_type": chat_type.value
                    }
                )
                
            return chat_metadata
            
        except Exception as e:
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_chat_metadata_creation_failed",
                    1,
                    labels={"error": str(e)}
                )
            raise ChatCreationError(f"Failed to create chat metadata: {str(e)}") from e
    
    async def get_chat_metadata(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Get chat metadata for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Chat metadata
        """
        try:
            # Get from Strapi
            chat_metadata = await self.strapi_service.get_by_field("session_id", session_id)
            if not chat_metadata:
                raise ChatNotFoundError(f"Chat metadata for session {session_id} not found")
                
            return chat_metadata
            
        except Exception as e:
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_chat_metadata_get_failed",
                    1,
                    labels={"error": str(e)}
                )
            raise ChatError(f"Failed to get chat metadata: {str(e)}") from e
    
    async def store_message(
        self,
        session_id: str,
        message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store a chat message.
        
        Args:
            session_id: Session ID
            message: Message data
            
        Returns:
            Stored message
        """
        try:
            # Validate input
            if not session_id:
                raise ChatError("Session ID is required")
            if not message:
                raise ChatError("Message is required")
                
            # Store message in Weaviate
            message_data = {
                "session_id": session_id,
                "content": message.get("content", ""),
                "role": message.get("role", "user"),
                "timestamp": message.get("timestamp", datetime.now().isoformat()),
                "metadata": message.get("metadata", {})
            }
            
            stored_message = await self.weaviate_service.create(message_data)
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_message_stored",
                    1,
                    labels={
                        "session_id": session_id,
                        "role": message_data["role"]
                    }
                )
                
            return stored_message
            
        except Exception as e:
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_message_store_failed",
                    1,
                    labels={"error": str(e)}
                )
            raise ChatError(f"Failed to store message: {str(e)}") from e
            
            
    async def add_message(
        self,
        session_id: Union[str, UUID],
        message: ChatMessage
    ) -> Optional[ChatMessage]:
        """Add a message to a chat session."""
        try:
            # Add message to Strapi
            message_data = {
                "sessionId": str(session_id),
                "role": message.role,
                "content": message.content,
                "type": message.type.value,
                "metadata": message.metadata
            }
            
            saved_message = await self.strapi_service.create_message(message_data)
            
            # Add to vector store if content exists
            if message.content:
                await self.weaviate_service.add_object(
                    class_name=f"Chat_{session_id}",
                    properties={
                        "content": message.content,
                        "metadata": {
                            "role": message.role,
                            "type": message.type.value,
                            "timestamp": message.created_at.isoformat()
                        }
                    }
                )
                
            # Create chat message object
            chat_message = ChatMessage(
                id=saved_message["id"],
                session_id=str(session_id),
                role=saved_message["role"],
                content=saved_message["content"],
                type=saved_message["type"],
                metadata=saved_message["metadata"],
                created_at=datetime.fromisoformat(saved_message["createdAt"])
            )
            
            # Record event
            event = ChatEvent(
                type="message_added",
                session_id=str(session_id),
                data=chat_message.to_dict(),
                timestamp=datetime.now()
            )
            self._session_events[str(session_id)].append(event)
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_message_added",
                    1,
                    labels={
                        "session_id": str(session_id),
                        "message_type": message.type.value,
                        "role": message.role
                    }
                )
                
            return chat_message
            
        except Exception as e:
            self.logger.error(f"Failed to add chat message: {str(e)}")
            raise ChatError(f"Failed to add chat message: {str(e)}") from e
            
    async def get_messages(
        self,
        session_id: Union[str, UUID],
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ChatMessage]:
        """Get messages from a chat session."""
        try:
            # Get from Strapi
            messages = await self.strapi_service.list_messages(
                session_id=str(session_id),
                limit=limit,
                offset=offset,
                filters=filters
            )
            
            # Convert to chat message objects
            return [
                ChatMessage(
                    id=message["id"],
                    session_id=str(session_id),
                    role=message["role"],
                    content=message["content"],
                    type=message["type"],
                    metadata=message["metadata"],
                    created_at=datetime.fromisoformat(message["createdAt"])
                )
                for message in messages
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get chat messages: {str(e)}")
            return []
            
    async def search_messages(
        self,
        session_id: Union[str, UUID],
        query: str,
        limit: int = 10
    ) -> List[ChatMessage]:
        """Search messages in a chat session using vector similarity."""
        try:
            # Search in Weaviate
            results = await self.weaviate_service.search(
                query=query,
                properties=["content"],
                filters={"path": ["session_id"], "operator": "Equal", "valueString": str(session_id)},
                limit=limit
            )
            
            # Convert to chat message objects
            messages = []
            for result in results:
                message_data = await self.strapi_service.get_message_by_content(
                    session_id=str(session_id),
                    content=result["content"]
                )
                if message_data:
                    messages.append(ChatMessage(
                        id=message_data["id"],
                        session_id=str(session_id),
                        role=message_data["role"],
                        content=message_data["content"],
                        type=message_data["type"],
                        metadata=message_data["metadata"],
                        created_at=datetime.fromisoformat(message_data["createdAt"])
                    ))
                    
            return messages
            
        except Exception as e:
            self.logger.error(f"Failed to search chat messages: {str(e)}")
            return []
            
    async def get_session_events(
        self,
        session_id: Union[str, UUID],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[ChatEvent]:
        """Get events for a chat session."""
        try:
            events = self._session_events.get(str(session_id), [])
            
            if start_time:
                events = [e for e in events if e.timestamp >= start_time]
            if end_time:
                events = [e for e in events if e.timestamp <= end_time]
                
            return events
            
        except Exception as e:
            self.logger.error(f"Failed to get chat session events: {str(e)}")
            return []
            