"""Base repository implementation."""
from typing import Dict, Any, Optional, Set, TypeVar, Generic, TYPE_CHECKING, ClassVar

from core.types.metrics import MetricsProtocol
from core.types.logging import LoggerProtocol
from core.config import AppConfig
from core.base.component import BaseComponent
from core.logging import BackendLogger

if TYPE_CHECKING:
    from core.cache.manager import CacheManager

T = TypeVar("T")


class BaseRepository(BaseComponent, Generic[T]):
    """Base repository class."""
    
    # Required config fields with their types
    REQUIRED_CONFIG: ClassVar[Dict[str, type]] = {
        'cache_ttl': int,
        'batch_size': int,
        'max_retries': int,
    }

    def __init__(
        self,
        name: str,
        config: Optional[AppConfig] = None,
        metrics: Optional[MetricsProtocol] = None,
        cache: Optional["CacheManager"] = None,
        logger: Optional[LoggerProtocol] = None,
        dependencies: Optional[Set[str]] = None,
        **kwargs
    ):
        """Initialize repository.
        
        Args:
            name: Repository name
            config: Application configuration
            metrics: Optional metrics manager
            cache: Optional cache manager
            logger: Optional logger instance
            dependencies: Optional set of dependency names
        """
        required_config = kwargs.get("required_config", 
                                     kwargs.get("REQUIRED_CONFIG", {}))
                
        super().__init__(
            name=name,
            metrics=metrics,
            config=config,
            logger=logger,
            dependencies=dependencies
        )
        
        self.cache = cache
        
        # Get validated repository config
        self._repository_config = self._get_repository_config(required_config)
        
        # Initialize repository settings from validated config
        self._cache_ttl = self._repository_config.get('cache_ttl', 3600)  # 1 hour default
        self._batch_size = self._repository_config.get('batch_size', 100)
        self._max_retries = self._repository_config.get('max_retries', 3)
        
        # Update health status with config details
        self.update_health_details({
            "config": {
                "cache_ttl": self._cache_ttl,
                "batch_size": self._batch_size,
                "max_retries": self._max_retries
            }
        })
        
        if self.logger:
            self.logger.debug(
                f"{name} repository created",
                context="repository",
                dependencies=list(self.dependencies)
            )

    def _get_repository_config(self, required_config: Dict[str, type]={}) -> Dict[str, Any]:
        """Extract and validate repository configuration.
        
        Returns:
            Dict containing validated configuration with defaults
            
        This method should be overridden by subclasses to provide
        repository-specific configuration validation and extraction.
        """
        try:
            # Start with default configuration
            config = {
                'retention_days': self._config.get('retention_days', 30),
                'cache_ttl': self._config.get('cache_ttl', 3600),
                'batch_size': self._config.get('batch_size', 100),
                'max_retries': self._config.get('max_retries', 3)
            }
            
            # Add any required config fields with their defaults
            for field, field_type in required_config.items():
                if field not in config:
                    config[field] = self._config.get(field)
            
            # Validate fields and log warnings for missing or invalid types
            for field, field_type in required_config.items():
                if not config.get(field):
                    if self.logger:
                        self.logger.warning(
                            f"Missing config field: {field}, using default value",
                            context="repository",
                            field=field,
                            default_value=config[field]
                        )
                elif not isinstance(config.get(field), field_type):
                    if self.logger:
                        self.logger.warning(
                            f"Invalid type for config field {field}. Expected {field_type}, got {type(config[field])}. Attempting conversion.",
                            context="repository",
                            field=field,
                            expected_type=str(field_type),
                            actual_type=str(type(config[field]))
                        )
                    try:
                        # Attempt type conversion
                        config[field] = field_type(config.get(field))
                    except (ValueError, TypeError):
                        if self.logger:
                            self.logger.warning(
                                f"Could not convert {field} to {field_type}, using default value",
                                context="repository",
                                field=field,
                                value=config.get(field)
                            )
            
            return config
            
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"Failed to get repository config: {str(e)}",
                    context="repository",
                    error=str(e)
                )
            # Return default configuration
            return {
                'cache_ttl': 3600,
                'batch_size': 100,
                'max_retries': 3
            } 