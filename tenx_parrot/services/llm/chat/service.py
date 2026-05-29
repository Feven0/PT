"""Chat LLM service for managing chat-based language model interactions."""
from typing import Dict, List, Optional, Any, Set
from uuid import UUID

from core.base.service import BaseService
from core.config.base import AppConfig
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.types.metrics import MetricType
from core.errors.exceptions import ServiceError
from core.llm.chain.manager import ChainManager
from core.prompt.manager import PromptManager
from core.llm.client import LLMClient as LLMClientManager

from services.session.service import SessionManagementService


class ChatLLMError(ServiceError):
    """Chat LLM service error."""
    pass

class ChatLLMService(BaseService):
    """Service for managing chat-based language model interactions."""
    
    REQUIRED_CONFIG = {
        "model_name": str,
        "temperature": float,
        "max_tokens": int,
        "cache_ttl": int
    }
    
    def __init__(
        self,
        name: str,
        config: AppConfig,
        chain_manager: ChainManager,
        prompt_manager: PromptManager,
        llm_client_manager: LLMClientManager,
        session_service: SessionManagementService,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize chat LLM service.
        
        Args:
            name: Service name
            config: Application configuration
            chain_manager: Chain manager for LLM chains
            prompt_manager: Prompt manager for LLM prompts
            llm_client_manager: LLM client manager
            session_service: Session management service
            metrics: Optional metrics manager
            logger: Optional logger instance
            dependencies: Optional set of dependency names
        """
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies,
            required_config=self.REQUIRED_CONFIG
        )
        
        self.chain_manager = chain_manager
        self.prompt_manager = prompt_manager
        self.llm_client_manager = llm_client_manager
        self.session_service = session_service
        
        # Get validated config
        self._service_config = self._config
        
        # Initialize settings from config
        self.model_name = self._service_config.get("model_name", "gpt-3.5-turbo")
        self.temperature = self._service_config.get("temperature", 0.7)
        self.max_tokens = self._service_config.get("max_tokens", 1024)
        self.cache_ttl = self._service_config.get("cache_ttl", 3600)
        
        # Register metrics
        if self.metrics:
            self._register_metrics()
    
    def _register_metrics(self) -> None:
        """Register service metrics."""
        self.metrics.register_metric(
            f"{self.name}_requests_total",
            MetricType.COUNTER,
            "Total number of chat LLM requests",
            labels={"model": "", "status": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_tokens_total",
            MetricType.COUNTER,
            "Total number of tokens processed",
            labels={"model": "", "type": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_latency_seconds",
            MetricType.HISTOGRAM,
            "Latency of chat LLM requests in seconds",
            labels={"model": "", "operation": ""}
        )
    
    
    async def generate_chat_response(
        self,
        session_id: str,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a response to a user message in a chat session.
        
        Args:
            session_id: Session ID
            user_message: User message text
            context: Optional additional context
            
        Returns:
            Response containing generated text and metadata
            
        Raises:
            ChatLLMError: If generation fails
        """
        try:
            # Get session
            session = await self.session_service.get_session(session_id)
            if not session:
                raise ChatLLMError(f"Session {session_id} not found")
            
            # Get chat history
            chat_history = await self.session_service.get_session_messages(session_id)
            
            # Prepare context
            full_context = {
                "session_id": session_id,
                "user_id": str(session.user_id),
                "chat_history": chat_history
            }
            
            if context:
                full_context.update(context)
            
            # Get the appropriate chain
            chain = await self.chain_manager.get_chain("chat")
            
            # Execute chain
            start_time = time.time()
            result = await chain.execute(
                input_text=user_message,
                context=full_context,
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            duration = time.time() - start_time
            
            # Record metrics
            if self.metrics:
                self.metrics.increment(
                    f"{self.name}_requests_total",
                    labels={"model": self.model_name, "status": "success"}
                )
                
                self.metrics.histogram(
                    f"{self.name}_latency_seconds",
                    duration,
                    labels={"model": self.model_name, "operation": "generate"}
                )
                
                if "token_usage" in result:
                    self.metrics.increment(
                        f"{self.name}_tokens_total",
                        result["token_usage"].get("prompt_tokens", 0),
                        labels={"model": self.model_name, "type": "prompt"}
                    )
                    
                    self.metrics.increment(
                        f"{self.name}_tokens_total",
                        result["token_usage"].get("completion_tokens", 0),
                        labels={"model": self.model_name, "type": "completion"}
                    )
            
            # Store message in session
            await self.session_service.store_message(
                session_id=session_id,
                message={
                    "role": "assistant",
                    "content": result["text"],
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "model": self.model_name,
                        "token_usage": result.get("token_usage", {})
                    }
                }
            )
            
            return {
                "text": result["text"],
                "model": self.model_name,
                "token_usage": result.get("token_usage", {}),
                "session_id": session_id
            }
            
        except Exception as e:
            # Record error metrics
            if self.metrics:
                self.metrics.increment(
                    f"{self.name}_requests_total",
                    labels={"model": self.model_name, "status": "error"}
                )
            
            self.logger.error(
                f"Failed to generate chat response: {str(e)}",
                session_id=session_id,
                error=str(e)
            )
            
            raise ChatLLMError(f"Failed to generate chat response: {str(e)}")
    
    async def check_health(self) -> Dict[str, Any]:
        """Check service health.
        
        Returns:
            Health status information
        """
        health_info = {
            "status": "healthy",
            "details": {
                "model": self.model_name,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
        }
        
        try:
            # Check LLM client health
            client_health = await self.llm_client_manager.check_health()
            if client_health["status"] != "healthy":
                health_info["status"] = "degraded"
                health_info["details"]["client_health"] = client_health
            
            # Check chain manager health
            chain_health = await self.chain_manager.check_health()
            if chain_health["status"] != "healthy":
                health_info["status"] = "degraded"
                health_info["details"]["chain_health"] = chain_health
            
            return health_info
            
        except Exception as e:
            health_info["status"] = "unhealthy"
            health_info["details"]["error"] = str(e)
            return health_info 