"""Dependency injection container implementation."""
from typing import Dict, Any, Optional, Set, TYPE_CHECKING, TypeVar, Type
from datetime import datetime
import asyncio
import socketio
from functools import cached_property

from core.types.base import ComponentNames as CN
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.config import AppConfig
from core.base.registry import LifecycleRegistry
from core.resilience.retry import RetryManager
from core.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerManager
from core.resilience.rate_limiter import RateLimiter, RateLimiterManager

from core.alert.manager import AlertManager
from core.session.manager import SessionManager as CoreSessionManager
from core.cache.manager import CacheManager
from core.llm.client import LLMClient
from core.llm.audio.manager import AudioManager
from core.llm.chain.manager import ChainManager
from core.prompt.manager import PromptManager

from infrastructure.strapi.client import StrapiClient
from infrastructure.weaviate.client import WeaviateInfrastructureClient
from infrastructure.gdrive.client import GDriveClient
from infrastructure.aws.s3_client import S3Client
from infrastructure.storage.client import StorageInfrastructureClient

from repositories.user import UserRepository
from repositories.interview import InterviewRepository
from repositories.session import SessionRepository
from repositories.storage import StorageRepository
from repositories.analysis import AnalysisRepository
from repositories.admin import AdminRepository
from repositories.observer import ObserverRepository
from repositories.overall_observer import OverallObserverRepository
from repositories.prompt import PromptRepository
from repositories.llm_metrics import LLMMetricsRepository

from services.user import UserService
from services.chat.service import ChatService
from services.interview.service import InterviewService
from services.observer.service import ObserverService
from services.storage import StorageService
from services.analysis import AnalysisService
from services.webrtc import WebRTCService
from services.session.service import SessionManagementService
from services.admin.service import AdminService
from services.llm_metrics import LLMMetricsService
from core.websocket.socketio_manager import SocketIOManager
from services.llm.chat.service import ChatLLMService
from services.llm.interview.service import InterviewLLMService


logger = BackendLogger(name="di_container").get_logger()


class ContainerError(Exception):
    """Base class for container errors."""
    pass


class DependencyError(ContainerError):
    """Error raised when dependencies are missing or invalid."""
    pass


T = TypeVar('T')

class ComponentAccessor:
    """Descriptor for type-safe component access."""
    
    def __init__(self, component_type: Type[T]):
        self.component_type = component_type
        self.name = None

    def __set_name__(self, owner, name):
        """Set descriptor name when class is created."""
        self.name = name

    def __get__(self, instance, owner=None) -> T:
        """Get component with type validation."""
        if instance is None:
            return self
            
        component = instance._components.get(self.name)
        if component is None:
            raise ValueError(f"Component '{self.name}' not registered")
            
        if not isinstance(component, self.component_type):
            raise TypeError(
                f"Component '{self.name}' has incorrect type. "
                f"Expected {self.component_type.__name__}, got {type(component).__name__}"
            )
            
        return component
    

class Container:
    """Dependency injection container with type-safe access."""
    
    def __init__(self, config: AppConfig):
        """Initialize container.
        
        Args:
            config: Application configuration
        """
        self._validate_config(config)
        self.config = config
        self.logger = None
        self.metrics_manager = None
        self.alert_manager = None
        self.core_session_manager = None
        self.registry = LifecycleRegistry(config)
        self._components: Dict[str, Any] = {}
        self._initialized_components: Set[str] = set()
        
        # Initialize logger
        self.logger = BackendLogger(name="di_container").get_logger()
        
        # Initialize all components in correct order
        self._init_components()

    def _validate_config(self, config: AppConfig) -> None:
        """Validate required configuration.
        
        Args:
            config: Application configuration
            
        Raises:
            ValueError: If required configuration is missing
        """
        required_configs = {
            'name': 'Application name',
            'version': 'Application version',
            'server.host': 'Server host',
            'server.port': 'Server port',
        }
        
        for key, desc in required_configs.items():
            parts = key.split('.')
            value = getattr(config, parts[0])
            if len(parts) > 1:
                for part in parts[1:]:
                    value = getattr(value, part, None)
            if not value:
                raise ValueError(f"Missing required config: {key} ({desc})")

    def _validate_dependencies(self, name: str, dependencies: Set[str]) -> None:
        """Validate component dependencies.
        
        Args:
            name: Component name
            dependencies: Required dependencies
            
        Raises:
            DependencyError: If dependencies are missing or invalid
        """
        if not dependencies:
            return

        missing = dependencies - set(self._components.keys())
        if missing:
            raise DependencyError(
                f"Component {name} missing required dependencies: {missing}"
            )

        # Check if dependencies are properly initialized
        uninitialized = dependencies - self._initialized_components
        if uninitialized:
            raise DependencyError(
                f"Component {name} has uninitialized dependencies: {uninitialized}"
            )

    def _register_component(self, 
                            name: str, 
                            instance: Any, 
                            dependencies: Optional[Set[str]] = set()) -> None:
        """Register component with validation.
        
        Args:
            name: Component name
            instance: Component instance
            dependencies: Component dependencies
            
        Raises:
            DependencyError: If dependencies are invalid
            ValueError: If component already exists
        """
        try:
            # Validate dependencies before registration
            # Here we ensure dependencies are already in the instance
            self._validate_dependencies(name, dependencies)
            
            # Check for duplicate registration
            if name in self._components:
                raise ValueError(f"Component already registered: {name}")
            
            # Register component
            self._components[name] = instance

            # Register component in registry - dependencies are already in the instance
            self.registry.register(name, instance)
            self._initialized_components.add(name)

            logger.info(
                f"{name} container registered",
                context="di_container",
                dependencies=list(dependencies)
            )            
            
        except Exception as e:
            logger.error(
                f"{name} container registration failed",
                context="di_container",
                error=str(e)
            )
            raise

    def _cleanup_failed_initialization(self) -> None:
        """Cleanup after failed initialization."""
        logger.info("starting_failed_initialization_cleanup")
        
        # Cleanup components in reverse initialization order
        for name in reversed(list(self._initialized_components)):
            try:
                component = self._components[name]
                if hasattr(component, 'cleanup'):
                    # Schedule cleanup for async components
                    if asyncio.iscoroutinefunction(component.cleanup):
                        asyncio.create_task(component.cleanup())
                    else:
                        component.cleanup()
                del self._components[name]
                self._initialized_components.remove(name)
                logger.info(
                    "component_cleaned_up",
                    component=name
                )
            except Exception as e:
                logger.error(
                    "component_cleanup_failed",
                    component=name,
                    error=str(e)
                )

    def _init_components(self) -> None:
        """Initialize all components in correct dependency order."""
        try:
            # 1. Core managers (no dependencies)
            self._init_core_managers()
            
            # 2. Infrastructure (depends on core)
            self._init_infrastructure()
            
            # 3. Repositories (depends on infrastructure)
            self._init_repositories()
            
            # 4. Services (depends on repositories)
            self._init_services()
            
            
            logger.info(
                "components_initialized",
                total_components=len(self._components)
            )
            
        except Exception as e:
            logger.error(
                "component_initialization_failed",
                error=str(e)
            )
            # Handle cleanup synchronously but schedule async cleanups
            self._cleanup_failed_initialization()
            raise ContainerError(f"Failed to initialize components: {e}")

    def _init_core_managers(self) -> None:
        """Initialize core managers."""
        try:                        
            # Initialize metrics manager first
            self.metrics_manager = MetricsManager(
                name=CN.metrics_manager,
                config=self.config.metrics
            )
            self._register_component(
                CN.metrics_manager,
                self.metrics_manager
            )
            
            # Initialize cache manager
            self.cache_manager = CacheManager(
                name=CN.cache_manager,
                config=self.config,
                metrics=self.metrics_manager,
                dependencies={
                    CN.metrics_manager
                }
            )
            self._register_component(
                CN.cache_manager,
                self.cache_manager
            )
                        
            # Initialize alert manager
            self.alert_manager = AlertManager(
                name=CN.alert_manager,
                config=self.config,
                metrics=self.metrics_manager,
                dependencies={
                    CN.metrics_manager
                }
            )
            self._register_component(
                CN.alert_manager,
                self.alert_manager
            )
            
            # Initialize core session manager
            self.core_session_manager = CoreSessionManager(
                name=CN.core_session_manager,
                config=self.config,
                metrics=self.metrics_manager,
                dependencies={
                    CN.metrics_manager
                }
            )
            self._register_component(
                CN.core_session_manager,
                self.core_session_manager
            )                        
            
            # Initialize retry manager
            self.retry_manager = RetryManager(
                name=CN.retry_manager,
                config=self.config,
                metrics=self.metrics_manager,
                dependencies={
                    CN.metrics_manager
                }
            )
            self._register_component(
                CN.retry_manager,
                self.retry_manager
            )
            
            # Initialize circuit breaker manager
            self.circuit_breaker_manager = CircuitBreakerManager(
                name=CN.circuit_breaker_manager,
                config=self.config,
                metrics=self.metrics_manager,
                dependencies={
                    CN.metrics_manager
                }
            )
            self._register_component(
                CN.circuit_breaker_manager,
                self.circuit_breaker_manager
            )
            
            # Initialize rate limiter manager
            self.rate_limiter_manager = RateLimiterManager(
                name=CN.rate_limiter_manager,
                config=self.config,
                metrics=self.metrics_manager,
                dependencies={
                    CN.metrics_manager
                }
            )
            self._register_component(
                CN.rate_limiter_manager,
                self.rate_limiter_manager
            )
            
            # Initialize SocketIO manager
            self.socketio_manager = SocketIOManager(
                cors_allowed_origins=self.config.cors.allow_origins,
                socketio_path=self.config.websocket.path
            )
            self._register_component(
                CN.socketio_manager,
                self.socketio_manager
            )            
            
            # Initialize LLM client
            self.llm_manager = LLMClient(
                name=CN.llm_manager,
                config=self.config.llm_manager,
                metrics=self.metrics_manager,
                dependencies={
                    CN.metrics_manager
                }
            )
            self._register_component(
                CN.llm_manager,
                self.llm_manager
            )

            # Initialize chain manager
            self.chain_manager = ChainManager(
                name=CN.chain_manager,
                config=self.config,
                metrics=self.metrics_manager,
                llm_client=self.llm_manager,
                dependencies={
                    CN.llm_manager
                }
            )
            self._register_component(
                CN.chain_manager, 
                self.chain_manager              
            )

            # Initialize managers that depend on LLM client
            self.audio_manager = AudioManager(
                name=CN.audio_manager,
                config=self.config,
                metrics=self.metrics_manager,
                llm_client=self.llm_manager,
                dependencies={
                    CN.llm_manager
                }
            )
            self._register_component(
                CN.audio_manager, 
                self.audio_manager              
            )

            self.prompt_manager = PromptManager(
                name=CN.prompt_manager,
                config=self.config,
                metrics=self.metrics_manager,
                dependencies={
                    CN.llm_manager
                }
            )
            self._register_component(
                CN.prompt_manager, 
                self.prompt_manager
            )      

            self.logger.info(
                "all_managers_registered",
                components=list(self._initialized_components),
                fg='pink'
            )
                  
        except Exception as e:
            self.logger.error(f"Failed to initialize core managers: {str(e)}")
            self._cleanup_failed_initialization()
            raise

    def _init_infrastructure(self) -> None:
        """Initialize infrastructure clients."""
        try:
            # 1. S3 client
            self.s3_client = S3Client(
                name=CN.s3_client,
                config=self.config,
                metrics=self.metrics_manager,
                retry=self.retry_manager,
                circuit_breaker=self.circuit_breaker_manager,
                rate_limiter=self.rate_limiter_manager,
                alert_manager=self.alert_manager,
                dependencies={
                    CN.metrics_manager,
                    CN.circuit_breaker_manager,
                    CN.retry_manager,
                    CN.rate_limiter_manager,
                    CN.alert_manager
                }
            )
            self._register_component(
                CN.s3_client,
                self.s3_client
            )
            
            # 2. GDrive client
            # self.gdrive_client = GDriveClient(
            #     name=CN.gdrive_client,
            #     config=self.config,
            #     metrics=self.metrics_manager,
            #     retry=self.retry_manager,
            #     circuit_breaker=self.circuit_breaker_manager,
            #     rate_limiter=self.rate_limiter_manager,
            #     alert_manager=self.alert_manager,
            #     dependencies={
            #         CN.metrics_manager,
            #         CN.circuit_breaker_manager,
            #         CN.retry_manager,
            #         CN.rate_limiter_manager,
            #         CN.alert_manager
            #     }
            # )
            # self._register_component(
            #     CN.gdrive_client,
            #     self.gdrive_client
            # )

            # 3. Strapi client
            self.strapi_client = StrapiClient(
                name=CN.strapi_client,
                config=self.config,
                metrics=self.metrics_manager,
                retry=self.retry_manager,
                circuit_breaker=self.circuit_breaker_manager,
                rate_limiter=self.rate_limiter_manager,
                alert_manager=self.alert_manager,
                dependencies={
                    CN.metrics_manager,
                    CN.circuit_breaker_manager,
                    CN.retry_manager,
                    CN.rate_limiter_manager,
                    CN.alert_manager
                }
            )
            self._register_component(
                CN.strapi_client,
                self.strapi_client
            )

            # 4. Weaviate client
            self.weaviate_client = WeaviateInfrastructureClient(
                name=CN.weaviate_client,
                config=self.config,
                metrics=self.metrics_manager,
                retry=self.retry_manager,
                circuit_breaker=self.circuit_breaker_manager,
                rate_limiter=self.rate_limiter_manager,
                alert_manager=self.alert_manager,
                dependencies={
                    CN.metrics_manager,
                    CN.circuit_breaker_manager,
                    CN.retry_manager,
                    CN.rate_limiter_manager,
                    CN.alert_manager
                }
            )
            self._register_component(
                CN.weaviate_client,
                self.weaviate_client
            )

            # 5. Storage infrastructure client (depends on all other clients)
            # self.storage_infrastructure_client = StorageInfrastructureClient(
            #     name=CN.storage_infrastructure_client,
            #     config=self.config,
            #     metrics=self.metrics_manager,
            #     retry=self.retry_manager,
            #     circuit_breaker=self.circuit_breaker_manager,
            #     rate_limiter=self.rate_limiter_manager,
            #     s3_client=self.s3_client,
            #     gdrive_client=self.gdrive_client,
            #     strapi_client=self.strapi_client,
            #     weaviate_client=self.weaviate_client,
            #     dependencies={
            #         CN.metrics_manager,
            #         CN.retry_manager,
            #         CN.circuit_breaker_manager,
            #         CN.rate_limiter_manager,
            #         CN.s3_client,
            #         CN.gdrive_client,
            #         CN.strapi_client,
            #         CN.weaviate_client
            #     }
            # )
            # self._register_component(
            #     CN.storage_infrastructure_client,
            #     self.storage_infrastructure_client
            # )
            
            logger.info(
                "all_infrastructures_registered",
                components=list(self._initialized_components),
                fg='pink'
            )
            
        except Exception as e:
            logger.error(
                "infrastructure_initialization_failed",
                error=str(e)
            )
            raise

    def _init_repositories(self) -> None:
        """Initialize repositories in correct dependency order."""
        # Storage repository (depends on storage infrastructure)
        # self.storage_repository = StorageRepository(
        #     name=CN.storage_repository,
        #     config=self.config,
        #     metrics=self.metrics_manager,
        #     storage_client=self.storage_infrastructure_client,
        #     dependencies={
        #         CN.metrics_manager,
        #         CN.storage_infrastructure_client
        #     }
        # )
        # self._register_component(
        #     CN.storage_repository,
        #     self.storage_repository
        # )

        # Initialize user repository
        self.user_repository = UserRepository(
            name=CN.user_repository,
            config=self.config,
            metrics=self.metrics_manager,
            strapi_client=self.strapi_client,
            cache=self.cache_manager,
            rate_limiter=self.rate_limiter_manager,
            retry_manager=self.retry_manager,
            dependencies={
                CN.metrics_manager,
                CN.cache_manager,
                CN.strapi_client,
                CN.rate_limiter,
                CN.retry_manager
            }
        )
        self._register_component(
            CN.user_repository,
            self.user_repository
        )

        # Initialize interview repository
        self.interview_repository = InterviewRepository(
            name=CN.interview_repository,
            config=self.config,
            metrics=self.metrics_manager,
            cache=self.cache_manager,
            strapi_client=self.strapi_client,
            weaviate_client=self.weaviate_client,
            alert_manager=self.alert_manager,
            dependencies={
                CN.metrics_manager,
                CN.cache_manager,
                CN.strapi_client,
                CN.weaviate_client,
                CN.alert_manager
            }
        )
        self._register_component(
            CN.interview_repository,
            self.interview_repository
        )

        # Initialize session repository
        self.session_repository = SessionRepository(
            name=CN.session_repository,
            config=self.config,
            metrics=self.metrics_manager,
            cache=self.cache_manager,
            strapi_client=self.strapi_client,
            weaviate_client=self.weaviate_client,
            alert_manager=self.alert_manager,
            retry_manager=self.retry_manager,
            rate_limiter=self.rate_limiter_manager,
            dependencies={
                CN.metrics_manager,
                CN.cache_manager,
                CN.strapi_client,
                CN.weaviate_client,
                CN.alert_manager,
                CN.retry_manager,
                CN.rate_limiter
            }
        )
        self._register_component(
            CN.session_repository,
            self.session_repository
        )

        # Initialize analysis repository
        self.analysis_repository = AnalysisRepository(
            name=CN.analysis_repository,
            config=self.config,
            metrics=self.metrics_manager,
            cache=self.cache_manager,
            strapi_client=self.strapi_client,
            weaviate_client=self.weaviate_client,
            alert_manager=self.alert_manager,
            dependencies={
                CN.metrics_manager,
                CN.cache_manager,
                CN.strapi_client,
                CN.weaviate_client,
                CN.alert_manager
            }
        )
        self._register_component(
            CN.analysis_repository,
            self.analysis_repository
        )

        # Initialize admin repository
        self.admin_repository = AdminRepository(
            name=CN.admin_repository,
            config=self.config,
            metrics=self.metrics_manager,
            cache=self.cache_manager,
            strapi_client=self.strapi_client,
            alert_manager=self.alert_manager,
            dependencies={
                CN.metrics_manager,
                CN.cache_manager,
                CN.strapi_client,
                CN.alert_manager
            }
        )
        self._register_component(
            CN.admin_repository,
            self.admin_repository
        )

        # Initialize observer repository
        self.observer_repository = ObserverRepository(
            name=CN.observer_repository,
            config=self.config,
            metrics=self.metrics_manager,
            cache=self.cache_manager,
            strapi_client=self.strapi_client,
            alert_manager=self.alert_manager,
            dependencies={
                CN.metrics_manager,
                CN.cache_manager,
                CN.strapi_client,
                CN.alert_manager
            }
        )
        self._register_component(
            CN.observer_repository,
            self.observer_repository
        )

        # Initialize overall observer repository
        self.overall_observer_repository = OverallObserverRepository(
            name=CN.overall_observer_repository,
            config=self.config,
            metrics=self.metrics_manager,
            cache=self.cache_manager,
            strapi_client=self.strapi_client,
            alert_manager=self.alert_manager,
            dependencies={
                CN.metrics_manager,
                CN.cache_manager,
                CN.strapi_client,
                CN.alert_manager
            }
        )
        self._register_component(
            CN.overall_observer_repository,
            self.overall_observer_repository
        )

        # Initialize prompt repository
        self.prompt_repository = PromptRepository(
            name=CN.prompt_repository,
            config=self.config,
            strapi_client=self.strapi_client,
            weaviate_client=self.weaviate_client,            
            metrics=self.metrics_manager,
            cache=self.cache_manager,
            alert_manager=self.alert_manager,
            dependencies={
                CN.metrics_manager,
                CN.cache_manager,
                CN.strapi_client,
                CN.weaviate_client,
                CN.strapi_client,
                CN.alert_manager
            }
        )
        self._register_component(
            CN.prompt_repository,
            self.prompt_repository
        )

        # Initialize LLM metrics repository
        self.llm_metrics_repository = LLMMetricsRepository(
            name=CN.llm_metrics_repository,
            config=self.config,
            metrics=self.metrics_manager,
            cache=self.cache_manager,
            strapi_client=self.strapi_client,
            alert_manager=self.alert_manager,
            dependencies={
                CN.metrics_manager,
                CN.cache_manager,
                CN.strapi_client,
                CN.alert_manager
            }
        )
        self._register_component(
            CN.llm_metrics_repository,
            self.llm_metrics_repository
        )

        self.logger.info(
            "all_repositories_registered",
            components=list(self._initialized_components),
            fg='pink'
        )

    def _init_services(self) -> None:
        """Initialize services in correct dependency order."""
        # Initialize LLM metrics service
        self.llm_metrics_service = LLMMetricsService(
            name=CN.llm_metrics_service,
            config=self.config,
            metrics=self.metrics_manager,
            llm_metrics_repository=self.llm_metrics_repository,
            dependencies={
                CN.metrics_manager,
                CN.llm_metrics_repository
            }
        )
        self._register_component(
            CN.llm_metrics_service,
            self.llm_metrics_service
        )

        # Initialize session service
        self.session_service = SessionManagementService(
            name=CN.session_service,
            config=self.config,
            session_repository=self.session_repository,
            observer_repository=self.observer_repository,
            cache=self.cache_manager,
            socketio_manager=self.socketio_manager,
            dependencies={
                CN.session_repository,
                CN.observer_repository,
                CN.cache_manager,
                CN.socketio_manager
            }
        )
        self._register_component(
            CN.session_service,
            self.session_service
        )

        # Initialize chat LLM service
        self.chat_llm_service = ChatLLMService(
            name=CN.chat_llm_service,
            config=self.config,            
            chain_manager=self.chain_manager,
            prompt_manager=self.prompt_manager,
            llm_client_manager=self.llm_manager,
            session_service=self.session_service,
            metrics=self.metrics_manager,
            dependencies={
                CN.metrics_manager,
                CN.chain_manager,
                CN.prompt_manager,
                CN.llm_manager,
                CN.session_service
            }
        )
        self._register_component(
            CN.chat_llm_service,
            self.chat_llm_service
        )

        # Initialize interview LLM service
        self.interview_llm_service = InterviewLLMService(
            name=CN.interview_llm_service,
            config=self.config,
            chain_manager=self.chain_manager,
            prompt_manager=self.prompt_manager,
            llm_client_manager=self.llm_manager,
            session_service=self.session_service,
            socketio_manager=self.socketio_manager,
            metrics=self.metrics_manager,
            dependencies={
                CN.metrics_manager,
                CN.chain_manager,
                CN.prompt_manager,
                CN.llm_manager,
                CN.session_service,
                CN.socketio_manager
            }
        )
        self._register_component(
            CN.interview_llm_service,
            self.interview_llm_service
        )

        self.observer_service = ObserverService(
            name=CN.observer_service,
            config=self.config,
            observer_repository=self.observer_repository,
            overall_observer_repository=self.overall_observer_repository,
            metrics=self.metrics_manager,
            dependencies={
                CN.observer_repository,
                CN.overall_observer_repository,
                CN.metrics_manager
            }
        )
        self._register_component(
            CN.observer_service,
            self.observer_service
        )

        # Initialize interview service
        self.interview_service = InterviewService(
            name=CN.interview_service,
            config=self.config,            
            session_service=self.session_service,
            interview_llm_service=self.interview_llm_service,
            observer_service=self.observer_service,
            socketio_manager=self.socketio_manager,
            metrics=self.metrics_manager,
            dependencies={
                CN.metrics_manager,
                CN.session_service,
                CN.interview_llm_service,
                CN.observer_service,
                CN.socketio_manager
            }
        )
        self._register_component(
            CN.interview_service,
            self.interview_service
        )

        # Initialize analysis service
        self.analysis_service = AnalysisService(
            name=CN.analysis_service,
            config=self.config,
            metrics=self.metrics_manager,
            alert_manager=self.alert_manager,
            cache_manager=self.cache_manager,
            interview_service=self.interview_service,
            session_service=self.session_service,
            user_repository=self.user_repository,
            analysis_repository=self.analysis_repository,
            dependencies={
                CN.metrics_manager,
                CN.alert_manager,
                CN.cache_manager,
                CN.interview_service,
                CN.session_service,
                CN.user_repository,
                CN.analysis_repository
            }
        )
        self._register_component(
            CN.analysis_service,
            self.analysis_service
        )

        # Initialize admin service
        self.admin_service = AdminService(
            name=CN.admin_service,
            config=self.config,
            admin_repository=self.admin_repository,
            metrics=self.metrics_manager,
            alert_manager=self.alert_manager,
            dependencies={
                CN.metrics_manager,
                CN.alert_manager,
                CN.admin_repository
            }
        )
        self._register_component(
            CN.admin_service,
            self.admin_service
        )

        # Initialize WebRTC service
        self.webrtc_service = WebRTCService(
            name=CN.webrtc_service,
            config=self.config,
            metrics=self.metrics_manager,
            logger=self.logger,
            socketio_manager=self.socketio_manager,
            dependencies={
                CN.metrics_manager,
                CN.socketio_manager
            }
        )
        self._register_component(
            CN.webrtc_service,
            self.webrtc_service
        )

        self.logger.info(
            "all_services_registered",
            components=list(self._initialized_components),
            fg='pink'
        )

    def get_middleware_config(self, name: str) -> Dict[str, Any]:
        """Get middleware configuration.
        
        Args:
            name: Middleware name
            
        Returns:
            Middleware configuration
        """
        if name not in self._components:
            return {}
            
        if name == 'cors':
            return self.config.cors.model_dump()
            
        return self._components[name].get_config()
        
    async def initialize(self) -> None:
        """Initialize container components."""
        logger.info(
            "initializing_container",
            context="initialize_di_container",
            fg='green'
        )
        await self.registry.initialize()
        
        
    async def start(self) -> None:
        """Start container components."""
        logger.info(
            "starting_container",
            context="di_container"
        )
        await self.registry.start()
        
            
    async def stop(self) -> None:
        """Stop container components."""
        logger.info(
            "stopping_container",
            context="di_container"
        )
        try:
            # Stop all other components
            await asyncio.wait_for(
                self.registry.stop(),
                timeout=10.0  # 10 second timeout for entire stop operation
            )
        except asyncio.TimeoutError:
            logger.error(
                "container_stop_timeout",
                context="di_container"
            )
        except Exception as e:
            logger.error(
                "container_stop_failed",
                context="di_container",
                error=str(e)
            )
            
    async def cleanup(self) -> None:
        """Clean up container resources."""
        logger.info(
            "cleaning_up_container",
            context="di_container"
        )
        
        try:
            # Get components in reverse initialization order
            cleanup_order = reversed(list(self._initialized_components))
  
            # Then cleanup other components
            for name in cleanup_order:
                component = self._components.get(name)
                if component:
                    if hasattr(component, 'cleanup'):
                        try:
                            if asyncio.iscoroutinefunction(component.cleanup):
                                await asyncio.wait_for(
                                    component.cleanup(),
                                    timeout=5.0  # 5 second timeout per component
                                )
                            else:
                                component.cleanup()
                            logger.info(
                                "component_cleaned_up",
                                component=name
                            )
                        except asyncio.TimeoutError:
                            logger.error(
                                "component_cleanup_timeout",
                                component=name
                            )
                        except Exception as e:
                            logger.error(
                                "component_cleanup_failed",
                                component=name,
                                error=str(e)
                            )
            
            # Clear container state
            self._components.clear()
            self._initialized_components.clear()
            
            # Clear registry state with timeout
            try:
                await asyncio.wait_for(
                    self.registry.cleanup(),
                    timeout=5.0  # 5 second timeout for registry cleanup
                )
            except asyncio.TimeoutError:
                logger.error("registry_cleanup_timeout")
            except Exception as e:
                logger.error(f"registry_cleanup_error: {str(e)}")
            
            logger.info("container_cleanup_completed")
            
        except Exception as e:
            logger.error(
                "container_cleanup_failed",
                error=str(e)
            )
            raise

    # Add type-safe component accessors
    metrics_manager = ComponentAccessor(MetricsManager)
    alert_manager = ComponentAccessor(AlertManager)
    cache_manager = ComponentAccessor(CacheManager)
    retry_manager = ComponentAccessor(RetryManager)
    circuit_breaker_manager = ComponentAccessor(CircuitBreakerManager)
    rate_limiter_manager = ComponentAccessor(RateLimiterManager)
    
    # Core managers
    session_manager = ComponentAccessor(CoreSessionManager)
    socketio_manager = ComponentAccessor(SocketIOManager)
    llm_manager = ComponentAccessor(LLMClient)
    audio_manager = ComponentAccessor(AudioManager)
    chain_manager = ComponentAccessor(ChainManager)
    prompt_manager = ComponentAccessor(PromptManager)
    
    # Infrastructure clients
    strapi_client = ComponentAccessor(StrapiClient)
    weaviate_client = ComponentAccessor(WeaviateInfrastructureClient)
    gdrive_client = ComponentAccessor(GDriveClient)
    s3_client = ComponentAccessor(S3Client)
    storage_client = ComponentAccessor(StorageInfrastructureClient)
    
    # Repositories
    user_repository = ComponentAccessor(UserRepository)
    interview_repository = ComponentAccessor(InterviewRepository)
    session_repository = ComponentAccessor(SessionRepository)
    storage_repository = ComponentAccessor(StorageRepository)
    analysis_repository = ComponentAccessor(AnalysisRepository)
    admin_repository = ComponentAccessor(AdminRepository)
    observer_repository = ComponentAccessor(ObserverRepository)
    overall_observer_repository = ComponentAccessor(OverallObserverRepository)
    prompt_repository = ComponentAccessor(PromptRepository)
    llm_metrics_repository = ComponentAccessor(LLMMetricsRepository)
    
    # Services
    user_service = ComponentAccessor(UserService)
    chat_llm_service = ComponentAccessor(ChatLLMService)
    interview_llm_service = ComponentAccessor(InterviewLLMService)
    chat_service = ComponentAccessor(ChatService)
    interview_service = ComponentAccessor(InterviewService)
    storage_service = ComponentAccessor(StorageService)
    analysis_service = ComponentAccessor(AnalysisService)
    webrtc_service = ComponentAccessor(WebRTCService)
    session_service = ComponentAccessor(SessionManagementService)
    admin_service = ComponentAccessor(AdminService)
    llm_metrics_service = ComponentAccessor(LLMMetricsService)
