"""Infrastructure factory module."""
from typing import Optional, Dict, Any

from core.base.lifecycle import LifecycleAware
from core.resilience.circuit_breaker import CircuitBreaker
from .strapi import StrapiDynamicService
from .weaviate.client import WeaviateClient
from core.logging import BackendLogger
from core.config import AppConfig

class StorageClientFactory:
    """Factory for storage client creation."""
    
    @staticmethod
    def create_client(
        storage_type: str,
        config: Dict[str, Any],
        use_resilience: bool = True,
        circuit_breaker_config: Optional[Dict[str, Any]] = None,
        logger: Optional[BackendLogger] = None
    ) -> LifecycleAware:
        """Create storage client based on configuration."""
        # Create base client
        if not logger:
            logger = BackendLogger(__name__)
        logger.name = "storage_client"
        logger.level = "ERROR"
        logger.use_colors = True
        logger = logger.get_logger()


        if storage_type == "strapi":
            client = StrapiDynamicService(
                api_root=config["api_root"],
                auth_token=config["auth_token"],
                collection=config.get("collection", "interviews")
            )
        elif storage_type == "weaviate":
            client = WeaviateClient(
                host=config["host"],
                port=config["port"],
                scheme=config.get("scheme", "http"),
                collection=config.get("collection", "Interviews"),
                batch_size=config.get("batch_size", 100)
            )
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
            
        # Add resilience if enabled
        if use_resilience and circuit_breaker_config:
            return CircuitBreaker(
                client=client,
                failure_threshold=circuit_breaker_config.get("failure_threshold", 5),
                recovery_timeout=circuit_breaker_config.get("recovery_timeout", 30),
                half_open_timeout=circuit_breaker_config.get("half_open_timeout", 15)
            )
            
        return client