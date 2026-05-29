"""Interview LLM service for managing interview-specific language model interactions."""
from typing import Dict, List, Optional, Any, Set, Union
from uuid import UUID, uuid4
from datetime import datetime
import time
import json
import asyncio

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
from core.websocket.socketio_manager import SocketIOManager
from core.types.websocket import SocketEvent


class InterviewLLMError(ServiceError):
    """Interview LLM service error."""
    pass

class InterviewLLMService(BaseService):
    """Service for managing interview-specific language model interactions."""
    
    REQUIRED_CONFIG = {
        "model_name": str,
        "temperature": float,
        "max_tokens": int,
        "cache_ttl": int,
        "observer_model": str
    }
    
    def __init__(
        self,
        name: str,
        config: AppConfig,
        chain_manager: ChainManager,
        prompt_manager: PromptManager,
        llm_client_manager: LLMClientManager,
        session_service: SessionManagementService,
        socketio_manager: SocketIOManager,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize interview LLM service.
        
        Args:
            name: Service name
            config: Application configuration
            chain_manager: Chain manager for LLM chains
            prompt_manager: Prompt manager for LLM prompts
            llm_client_manager: LLM client manager
            session_service: Session management service
            socketio_manager: Socket.io manager
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
            REQUIRED_CONFIG=self.REQUIRED_CONFIG
        )
        
        self.chain_manager = chain_manager
        self.prompt_manager = prompt_manager
        self.llm_client_manager = llm_client_manager
        self.session_service = session_service
        self.socketio_manager = socketio_manager
        
        # Get validated config
        config_dict = self._config
        
        # Initialize LLM settings from validated config
        self.model_name = config_dict.get("model_name", "gpt-4")
        self.temperature = config_dict.get("temperature", 0.7)
        self.max_tokens = config_dict.get("max_tokens", 1024)
        self.cache_ttl = config_dict.get("cache_ttl", 3600)
        self.observer_model = config_dict.get("observer_model", "gpt-4")
        
        # Register metrics if available
        if self.metrics:
            self._register_metrics()
    
    def _register_metrics(self) -> None:
        """Register interview LLM metrics."""
        # Operation metrics
        self.metrics.register_metric(
            f"{self.name}_operations_total",
            MetricType.COUNTER,
            f"Total number of operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # LLM metrics
        self.metrics.register_metric(
            f"{self.name}_requests_total",
            MetricType.COUNTER,
            "Total number of interview LLM requests",
            labels={"model": "", "operation": "", "status": ""}
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
            "Latency of interview LLM requests in seconds",
            labels={"model": "", "operation": ""}
        )
        
        # Observer metrics
        self.metrics.register_metric(
            f"{self.name}_observations_total",
            MetricType.COUNTER,
            "Total number of interview observations",
            labels={"session_id": "", "type": ""}
        )
        
        # Error metrics
        self.metrics.register_metric(
            f"{self.name}_errors_total",
            MetricType.COUNTER,
            f"Total number of errors in {self.name}",
            labels={"error_type": "", "operation": ""}
        )
    
    async def generate_question(
        self,
        session_id: str,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate an interview question with streaming support.
        
        Args:
            session_id: Session ID
            user_message: User message text
            context: Optional additional context
            
        Returns:
            Generated question with metadata
        """
        try:
            # Get session
            session = await self.session_service.get_session(session_id)
            if not session:
                raise InterviewLLMError(f"Session {session_id} not found")
            
            # Get interview history
            interview_history = await self.session_service.get_session_messages(session_id)
            
            # Prepare context
            full_context = {
                "session_id": session_id,
                "user_id": str(session.user_id),
                "interview_history": interview_history
            }
            
            if context:
                full_context.update(context)
            
            # Get the appropriate chain
            chain = await self.chain_manager.get_chain("interview")
            
            # Create separate rooms for questions and analysis
            question_room = f"{session_id}_questions"
            analysis_room = f"{session_id}_analysis"
            
            # Execute chain with streaming
            start_time = time.time()
            
            # Stream the question generation
            async for chunk in chain.stream(
                input_text=user_message,
                context=full_context,
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            ):
                # Emit question chunk to question room
                await self.socketio_manager.emit(
                    SocketEvent.INTERVIEW_QUESTION_CHUNK,
                    {
                        "chunk": chunk,
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat()
                    },
                    room=question_room
                )
                
                # Generate and emit analysis in parallel
                analysis_task = asyncio.create_task(
                    self._generate_and_emit_analysis(
                        session_id=session_id,
                        question_chunk=chunk,
                        context=full_context,
                        analysis_room=analysis_room
                    )
                )
                
                # Wait for analysis to complete
                await analysis_task
            
            duration = time.time() - start_time
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "generate_question", "status": "success"}
                )
                
                self.metrics.record(
                    f"{self.name}_requests_total",
                    1,
                    labels={
                        "model": self.model_name, 
                        "operation": "generate", 
                        "status": "success"
                    }
                )
                
                self.metrics.record(
                    f"{self.name}_latency_seconds",
                    duration,
                    labels={"model": self.model_name, "operation": "generate"}
                )
            
            # Store message in session
            await self.session_service.store_message(
                session_id=session_id,
                message={
                    "role": "assistant",
                    "content": chunk,  # Use the final chunk
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "model": self.model_name,
                        "token_usage": {} #result.get("token_usage", {})
                    }
                }
            )
            
            # Create observation for this exchange
            await self.create_session_observation(
                session_id=session_id,
                user_message=user_message,
                assistant_message=chunk,  # Use the final chunk
                context=full_context
            )
            
            return {
                "text": chunk,  # Use the final chunk
                "model": self.model_name,
                "token_usage": {}, #result.get("token_usage", {}),
                "session_id": session_id
            }
            
        except Exception as e:
            # Record error metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "generate_question", "status": "error"}
                )
                
                self.metrics.record(
                    f"{self.name}_requests_total",
                    1,
                    labels={
                        "model": self.model_name, 
                        "operation": "generate", 
                        "status": "error"
                    }
                )
                
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "generate_question"}
                )
            
            self.logger.error(
                f"Failed to generate interview response: {str(e)}",
                session_id=session_id,
                error=str(e)
            )
            
            raise InterviewLLMError(f"Failed to generate interview response: {str(e)}")
            
    async def _generate_and_emit_analysis(
        self,
        session_id: str,
        question_chunk: str,
        context: Dict[str, Any],
        analysis_room: str
    ) -> None:
        """Generate and emit real-time analysis.
        
        Args:
            session_id: Session ID
            question_chunk: Current question chunk
            context: Full context
            analysis_room: Socket.io room for analysis
        """
        try:
            # Get the analysis chain
            chain = await self.chain_manager.get_chain("interview_analysis")
            
            # Generate analysis
            analysis = await chain.execute(
                input_text=question_chunk,
                context=context,
                model=self.observer_model,
                temperature=0.2,  # Lower temperature for more consistent analysis
                max_tokens=512
            )
            
            # Emit analysis
            await self.socketio_manager.emit(
                SocketEvent.INTERVIEW_ANALYSIS,
                {
                    "analysis": analysis["text"],
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": analysis.get("metadata", {})
                },
                room=analysis_room
            )
            
        except Exception as e:
            self.logger.error(
                f"Failed to generate analysis: {str(e)}",
                session_id=session_id,
                error=str(e)
            )
    
    async def create_session_observer(
        self,
        session_id: str,
        observer_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create an observer for a session.
        
        Args:
            session_id: Session ID
            observer_type: Type of observer to create
            config: Optional observer configuration
            
        Returns:
            Observer information
            
        Raises:
            InterviewLLMError: If observer creation fails
        """
        try:
            # Get session
            session = await self.session_service.get_session(session_id)
            if not session:
                raise InterviewLLMError(f"Session {session_id} not found")
            
            # Prepare observer config
            observer_config = {
                "type": observer_type,
                "model": self.observer_model,
                "created_at": datetime.now().isoformat()
            }
            
            if config:
                observer_config.update(config)
            
            # Create observer in session
            observer_id = str(uuid4())
            await self.session_service.create_observer(
                session_id=session_id,
                observer_id=observer_id,
                observer_config=observer_config
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_requests_total",
                    1,
                    labels={
                        "model": self.observer_model, 
                        "operation": "create_observer", 
                        "status": "success"
                    }
                )
            
            return {
                "observer_id": observer_id,
                "session_id": session_id,
                "type": observer_type,
                "config": observer_config
            }
            
        except Exception as e:
            # Record error metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_requests_total",
                    1,
                    labels={
                        "model": self.observer_model, 
                        "operation": "create_observer", 
                        "status": "error"
                    }
                )
                
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "create_observer"}
                )
            
            self.logger.error(
                f"Failed to create session observer: {str(e)}",
                session_id=session_id,
                observer_type=observer_type,
                error=str(e)
            )
            
            raise InterviewLLMError(f"Failed to create session observer: {str(e)}")
    
    async def create_session_observation(
        self,
        session_id: str,
        user_message: str,
        assistant_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create an observation for a session exchange.
        
        Args:
            session_id: Session ID
            user_message: User message
            assistant_message: Assistant message
            context: Optional additional context
            
        Returns:
            Observation information
            
        Raises:
            InterviewLLMError: If observation creation fails
        """
        try:
            # Get session
            session = await self.session_service.get_session(session_id)
            if not session:
                raise InterviewLLMError(f"Session {session_id} not found")
            
            # Get observers for this session
            observers = await self.session_service.get_session_observers(session_id)
            if not observers:
                # No observers, nothing to do
                return {"status": "skipped", "reason": "no_observers"}
            
            # Prepare exchange context
            exchange = {
                "user": user_message,
                "assistant": assistant_message,
                "timestamp": datetime.now().isoformat()
            }
            
            if context:
                exchange["context"] = context
            
            # For each observer, generate an observation
            observations = []
            
            for observer in observers:
                observer_type = observer.get("type", "general")
                observer_id = observer.get("id")
                
                # Get the appropriate chain for this observer type
                chain_name = f"observer_{observer_type}"
                try:
                    chain = await self.chain_manager.get_chain(chain_name)
                except:
                    # Fallback to general observer chain
                    chain = await self.chain_manager.get_chain("observer_general")
                
                # Execute chain
                start_time = time.time()
                result = await chain.execute(
                    input_text=f"User: {user_message}\nAssistant: {assistant_message}",
                    context={
                        "session_id": session_id,
                        "observer_type": observer_type,
                        "observer_id": observer_id,
                        "exchange": exchange
                    },
                    model=self.observer_model,
                    temperature=0.2,  # Lower temperature for more consistent observations
                    max_tokens=1024
                )
                duration = time.time() - start_time
                
                # Record metrics
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_requests_total",
                        1,
                        labels={
                            "model": self.observer_model, 
                            "operation": "create_observation", 
                            "status": "success"
                        }
                    )
                    
                    self.metrics.record(
                        f"{self.name}_latency_seconds",
                        duration,
                        labels={"model": self.observer_model, "operation": "observe"}
                    )
                    
                    self.metrics.record(
                        f"{self.name}_observations_total",
                        1,
                        labels={"session_id": session_id, "type": observer_type}
                    )
                
                # Create observation object
                observation = {
                    "id": str(uuid4()),
                    "observer_id": observer_id,
                    "observer_type": observer_type,
                    "session_id": session_id,
                    "exchange": exchange,
                    "observation": result["text"],
                    "created_at": datetime.now().isoformat(),
                    "metadata": {
                        "model": self.observer_model,
                        "token_usage": result.get("token_usage", {})
                    }
                }
                
                # Store observation
                await self.session_service.store_observation(
                    session_id=session_id,
                    observer_id=observer_id,
                    observation=observation
                )
                
                observations.append(observation)
            
            return {
                "session_id": session_id,
                "observations": observations,
                "count": len(observations)
            }
            
        except Exception as e:
            # Record error metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_requests_total",
                    1,
                    labels={
                        "model": self.observer_model, 
                        "operation": "create_observation", 
                        "status": "error"
                    }
                )
                
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "create_observation"}
                )
            
            self.logger.error(
                f"Failed to create session observation: {str(e)}",
                session_id=session_id,
                error=str(e)
            )
            
            raise InterviewLLMError(f"Failed to create session observation: {str(e)}")
    
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
            limit: Optional limit on number of observations
            offset: Optional offset for pagination
            
        Returns:
            List of observations
            
        Raises:
            InterviewLLMError: If retrieval fails
        """
        try:
            # Get session
            session = await self.session_service.get_session(session_id)
            if not session:
                raise InterviewLLMError(f"Session {session_id} not found")
            
            # Get observations
            observations = await self.session_service.get_session_observations(
                session_id=session_id,
                observer_id=observer_id,
                limit=limit,
                offset=offset
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_requests_total",
                    1,
                    labels={
                        "model": self.observer_model, 
                        "operation": "get_observations", 
                        "status": "success"
                    }
                )
                
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "get_observations", "status": "success"}
                )
            
            return observations
            
        except Exception as e:
            # Record error metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_requests_total",
                    1,
                    labels={
                        "model": self.observer_model, 
                        "operation": "get_observations", 
                        "status": "error"
                    }
                )
                
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "get_observations", "status": "error"}
                )
                
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "get_observations"}
                )
            
            self.logger.error(
                f"Failed to get session observations: {str(e)}",
                session_id=session_id,
                observer_id=observer_id,
                error=str(e)
            )
            
            raise InterviewLLMError(f"Failed to get session observations: {str(e)}")
    
    async def generate_session_summary(
        self,
        session_id: str,
        summary_type: str = "general"
    ) -> Dict[str, Any]:
        """Generate a summary for a session.
        
        Args:
            session_id: Session ID
            summary_type: Type of summary to generate
            
        Returns:
            Summary information
            
        Raises:
            InterviewLLMError: If summary generation fails
        """
        try:
            # Get session
            session = await self.session_service.get_session(session_id)
            if not session:
                raise InterviewLLMError(f"Session {session_id} not found")
            
            # Get session messages
            messages = await self.session_service.get_session_messages(session_id)
            
            # Get observations
            observations = await self.session_service.get_session_observations(session_id)
            
            # Prepare context
            context = {
                "session_id": session_id,
                "user_id": str(session.user_id),
                "messages": messages,
                "observations": observations,
                "summary_type": summary_type
            }
            
            # Get the appropriate chain
            chain_name = f"summary_{summary_type}"
            try:
                chain = await self.chain_manager.get_chain(chain_name)
            except:
                # Fallback to general summary chain
                chain = await self.chain_manager.get_chain("summary_general")
            
            # Execute chain
            start_time = time.time()
            result = await chain.execute(
                input_text=f"Generate a {summary_type} summary for session {session_id}",
                context=context,
                model=self.model_name,
                temperature=0.3,  # Lower temperature for more consistent summaries
                max_tokens=2048
            )
            duration = time.time() - start_time
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_requests_total",
                    1,
                    labels={
                        "model": self.model_name, 
                        "operation": "generate_summary", 
                        "status": "success"
                    }
                )
                
                self.metrics.record(
                    f"{self.name}_latency_seconds",
                    duration,
                    labels={"model": self.model_name, "operation": "summarize"}
                )
                
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "generate_summary", "status": "success"}
                )
            
            # Create summary object
            summary = {
                "id": str(uuid4()),
                "session_id": session_id,
                "summary_type": summary_type,
                "summary": result["text"],
                "created_at": datetime.now().isoformat(),
                "metadata": {
                    "model": self.model_name,
                    "token_usage": result.get("token_usage", {})
                }
            }
            
            # Store summary
            await self.session_service.store_summary(
                session_id=session_id,
                summary=summary
            )
            
            return summary
            
        except Exception as e:
            # Record error metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_requests_total",
                    1,
                    labels={
                        "model": self.model_name, 
                        "operation": "generate_summary", 
                        "status": "error"
                    }
                )
                
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "generate_summary", "status": "error"}
                )
                
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "generate_summary"}
                )
            
            self.logger.error(
                f"Failed to generate session summary: {str(e)}",
                session_id=session_id,
                summary_type=summary_type,
                error=str(e)
            )
            
            raise InterviewLLMError(f"Failed to generate session summary: {str(e)}")
    
    async def check_health(self) -> Dict[str, Any]:
        """Check service health.
        
        Returns:
            Health status information
        """
        health_info = {
            "status": "healthy",
            "details": {
                "model": self.model_name,
                "observer_model": self.observer_model,
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