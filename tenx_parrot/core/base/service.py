"""Base service implementation."""
from typing import Dict, List, Optional, Set, Union, Any, Type, TypeVar, Generic
from datetime import datetime, timezone
import asyncio

from pydantic import BaseModel, Field

from core.types.components import HealthStatus
from core.types.user import User
from core.config.base import AppConfig
from core.logging import BackendLogger

from core.types.metrics import MetricsProtocol
from core.types.logging import LoggerProtocol
from core.types.components import ComponentState
from core.base.manager import BaseManager
from core.telemetry.service_metrics import ServiceMetrics
from .component import BaseComponent

T = TypeVar("T")

class BaseService(BaseComponent, Generic[T]):
    """Base service class."""
    
    def __init__(
        self,
        name: str,
        config: Union[Dict[str, Any], 'AppConfig'],
        metrics: Optional[MetricsProtocol] = None,
        logger: Optional[LoggerProtocol] = None,
        dependencies: Optional[Set[str]] = None,
        **kwargs
    ):
        """Initialize service.
        
        Args:
            name: Service name
            config: Application configuration
            metrics: Optional metrics manager
            logger: Optional logger instance
            dependencies: Optional set of dependency names
            REQUIRED_CONFIG: Optional dictionary of required configuration fields
        """
        required_config = kwargs.get("required_config", 
                                     kwargs.get("REQUIRED_CONFIG", {}))
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies
        )
        
        # Initialize service configuration
        self._config = self._get_service_config(required_config)
        if not self._config.get("enabled"):
            self._state = ComponentState.DISABLED
            if self.logger:
                self.logger.warning(
                    "service_disabled",
                    service=name
                )
            return
            
        self._state = ComponentState.INITIALIZING
        self._state = ComponentState.CREATED

        # # Initialize service metrics
        # if metrics and self._config.get("metrics_enabled", True):        
        #     self._metrics = ServiceMetrics(                
        #         metrics=metrics,
        #         service_name=name
        #     )
            
        if self.logger:
            self.logger.info(
                f"{name} service_created",
                context="service",
                dependencies=list(self.dependencies)
            )
            
    def _get_service_config(self, REQUIRED_CONFIG: Dict[str, Any]={}) -> Any:
        """Get service-specific configuration.
        
        Override this method to return service-specific configuration.
        
        Returns:
            Service configuration
        """
        config = self.config

        try:
            # Validate required fields with warnings
            for field, field_type in REQUIRED_CONFIG.items():
                if field == "performance_settings":
                    perf_settings = {}
                    if config.get(field):
                        settings = config.get(field)
                        for subfield, subfield_type in field_type.items():
                            if settings.get(subfield):
                                value = settings.get(subfield)
                                if isinstance(value, subfield_type):
                                    perf_settings[subfield] = value
                                else:
                                    self.logger.warning(
                                        f"Invalid type for {subfield} in performance_settings",
                                        field=subfield,
                                        expected_type=str(subfield_type),
                                        actual_type=str(type(value))
                                    )
                            else:
                                self.logger.warning(
                                    f"Missing {subfield} in performance_settings",
                                    field=subfield
                                )
                    config["performance_settings"] = perf_settings
                else:
                    if config.get(field):
                        value = config.get(field)
                        if isinstance(value, field_type):
                            config[field] = value
                        else:
                            self.logger.warning(
                                f"Invalid type for {field}",
                                field=field,
                                expected_type=str(field_type),
                                actual_type=str(type(value))
                            )
                    else:
                        self.logger.warning(
                            f"Missing config field: {field}",
                            field=field
                        )

            return config
        
        except Exception as e:
            self.logger.error(
                "Failed to validate config for service",
                service=self.name,
                error=str(e)
            )
            return self.config

     
            
    def _get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        try:
            return getattr(self._service_config, key)
        except AttributeError:
            return default 