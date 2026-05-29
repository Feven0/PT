"""Storage service implementation."""
from typing import Dict, Any, Optional, Union, List, BinaryIO, Set
from datetime import datetime, timezone
from pathlib import Path

from core.logging import BackendLogger, LogFormat
from core.config import AppConfig
from core.telemetry.metrics import MetricsManager
from core.errors.exceptions import StorageError, NotFoundError
from core.types.components import HealthStatus, HealthStatusInfo
from core.types.base import ComponentNames as CN
from core.alert.manager import AlertManager
from core.base.service import BaseService
from repositories.storage import StorageRepository
from infrastructure.storage.client import StorageInfrastructureClient


# Initialize logger with custom colors
log_manager = BackendLogger(
    name="storage",
    format="text",
    colors={
        "storage": "bright_cyan",
        "s3": "bright_blue",
        "gdrive": "bright_magenta",
        "strapi": "bright_yellow",
        "weaviate": "bright_green"
    }
)
logger = log_manager.get_logger()


class StorageService(BaseService):
    """Storage service with unified storage management."""
    
    REQUIRED_CONFIG = {
        "max_file_size": int,
        "allowed_extensions": list,
        "performance_settings": {
            "batch_size": int,
            "max_concurrent_uploads": int,
            "cache_ttl": int
        }
    }
    
    def __init__(
        self,
        name: str,
        config: AppConfig,
        metrics: Optional[MetricsManager] = None,
        storage_repository: Optional[StorageRepository] = None,
        alert_manager: Optional[AlertManager] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize storage service.
        
        Args:
            config: Application configuration
            metrics: Optional metrics manager
            storage_repository: Optional storage repository
        """
        super().__init__(name=name, 
                         config=config, 
                         metrics=metrics, 
                         dependencies=dependencies)
        
        # Get validated config
        config_dict = self._get_service_config()
        
        # Set config values with defaults
        self.max_file_size = config_dict.get("max_file_size", 10485760)  # 10MB default
        self.allowed_extensions = config_dict.get("allowed_extensions", ["*"])
        
        # Performance settings
        perf_settings = config_dict.get("performance_settings", {})
        self.batch_size = perf_settings.get("batch_size", 100)
        self.max_concurrent_uploads = perf_settings.get("max_concurrent_uploads", 10)
        self.cache_ttl = perf_settings.get("cache_ttl", 3600)
        
        # Initialize storage repository
        self._storage = storage_repository
        self._alert_manager = alert_manager
         

    def _get_service_config(self) -> Dict[str, Any]:
        """Get and validate service configuration.
        
        Returns:
            Dict containing validated configuration with defaults
        """
        try:
            config_dict = {}
            
            # Get config from storage section
            if hasattr(self.config, "storage"):
                config = self.config.storage
                
                # Validate required fields with warnings
                for field, field_type in self.REQUIRED_CONFIG.items():
                    if field == "performance_settings":
                        perf_settings = {}
                        if hasattr(config, field):
                            settings = getattr(config, field)
                            for subfield, subfield_type in field_type.items():
                                if hasattr(settings, subfield):
                                    value = getattr(settings, subfield)
                                    if isinstance(value, subfield_type):
                                        perf_settings[subfield] = value
                                    else:
                                        logger.warning(
                                            f"Invalid type for {subfield} in performance_settings",
                                            field=subfield,
                                            expected_type=str(subfield_type),
                                            actual_type=str(type(value))
                                        )
                                else:
                                    logger.warning(
                                        f"Missing {subfield} in performance_settings",
                                        field=subfield
                                    )
                        config_dict["performance_settings"] = perf_settings
                    else:
                        if hasattr(config, field):
                            value = getattr(config, field)
                            if isinstance(value, field_type):
                                config_dict[field] = value
                            else:
                                logger.warning(
                                    f"Invalid type for {field}",
                                    field=field,
                                    expected_type=str(field_type),
                                    actual_type=str(type(value))
                                )
                        else:
                            logger.warning(
                                f"Missing config field: {field}",
                                field=field
                            )
            else:
                logger.warning("No storage configuration section found")
            
            return config_dict
            
        except Exception as e:
            logger.error(
                "Failed to validate config",
                error=str(e)
            )
            return {}

    async def _initialize(self) -> None:
        """Initialize storage service."""
        await self._storage.initialize()
        
    async def _cleanup(self) -> None:
        """Cleanup storage service."""
        await self._storage.cleanup()
        
    async def _check_health(self) -> HealthStatusInfo:
        """Check storage health.
        
        Returns:
            Health status information
        """
        health_info = HealthStatusInfo(
            status=HealthStatus.UNKNOWN,
            details={
                "metrics": {},
                "last_check": datetime.now(timezone.utc)
            }
        )
        
        try:
            # Get storage health
            storage_health = await self._storage.check_health()
            health_info.details["metrics"] = storage_health
            
            # Determine overall status
            provider_statuses = [
                provider["status"]
                for provider in storage_health.get("storage", {}).values()
            ]
            
            if all(status == "healthy" for status in provider_statuses):
                health_info.status = HealthStatus.HEALTHY
            elif any(status == "healthy" for status in provider_statuses):
                health_info.status = HealthStatus.DEGRADED
            else:
                health_info.status = HealthStatus.UNHEALTHY
                
        except Exception as e:
            logger.error(
                "health_check_failed",
                error=str(e)
            )
            health_info.update(
                status=HealthStatus.UNHEALTHY,
                details={
                    **health_info.details,
                    "error": str(e)
                }
            )
            
        # Log health status
        logger.info(
            "storage_health_status",
            format=LogFormat.TABLE,
            table_data={
                "Overall": {
                    "Status": health_info.status.value,
                    "Last Check": health_info.details["last_check"].isoformat()
                },
                **{
                    provider: {
                        "Status": info["status"],
                        "Is Primary": str(info.get("is_primary", False)),
                        "Error": info.get("error", "None")
                    }
                    for provider, info in health_info.details.get("metrics", {}).get("storage", {}).items()
                }
            },
            table_title="Storage Health Status"
        )
        
        return health_info
        
    async def upload_file(
        self,
        file_path: Union[str, Path],
        data: Union[bytes, BinaryIO],
        mime_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None
    ) -> str:
        """Upload file to storage.
        
        Args:
            file_path: File path
            data: File data or file-like object
            mime_type: Optional MIME type
            metadata: Optional metadata
            provider: Optional provider override
            
        Returns:
            Storage path
            
        Raises:
            StorageError: If upload fails
        """
        try:
            return await self._storage.upload_file(
                file_path=file_path,
                data=data,
                mime_type=mime_type,
                metadata=metadata,
                provider=provider
            )
        except Exception as e:
            logger.error(
                "upload_failed",
                error=str(e),
                file_path=file_path,
                provider=provider
            )
            raise
            
    async def download_file(
        self,
        file_path: Union[str, Path],
        provider: Optional[str] = None
    ) -> bytes:
        """Download file from storage.
        
        Args:
            file_path: File path
            provider: Optional provider override
            
        Returns:
            File data
            
        Raises:
            StorageError: If download fails
            NotFoundError: If file not found
        """
        try:
            return await self._storage.download_file(
                file_path=file_path,
                provider=provider
            )
        except Exception as e:
            logger.error(
                "download_failed",
                error=str(e),
                file_path=file_path,
                provider=provider
            )
            raise
            
    async def delete_file(
        self,
        file_path: Union[str, Path],
        provider: Optional[str] = None
    ) -> None:
        """Delete file from storage.
        
        Args:
            file_path: File path
            provider: Optional provider override
            
        Raises:
            StorageError: If deletion fails
        """
        try:
            await self._storage.delete_file(
                file_path=file_path,
                provider=provider
            )
        except Exception as e:
            logger.error(
                "delete_failed",
                error=str(e),
                file_path=file_path,
                provider=provider
            )
            raise
            
    async def list_files(
        self,
        directory: Union[str, Path] = "",
        provider: Optional[str] = None,
        recursive: bool = False
    ) -> List[str]:
        """List files in storage.
        
        Args:
            directory: Directory path
            provider: Optional provider override
            recursive: Whether to list recursively
            
        Returns:
            List of file paths
            
        Raises:
            StorageError: If listing fails
        """
        try:
            return await self._storage.list_files(
                directory=directory,
                provider=provider,
                recursive=recursive
            )
        except Exception as e:
            logger.error(
                "list_failed",
                error=str(e),
                directory=directory,
                provider=provider
            )
            raise
            
    async def move_file(
        self,
        source_path: Union[str, Path],
        destination_path: Union[str, Path],
        provider: Optional[str] = None
    ) -> None:
        """Move file in storage.
        
        Args:
            source_path: Source file path
            destination_path: Destination file path
            provider: Optional provider override
            
        Raises:
            StorageError: If move fails
        """
        try:
            await self._storage.move_file(
                source_path=source_path,
                destination_path=destination_path,
                provider=provider
            )
        except Exception as e:
            logger.error(
                "move_failed",
                error=str(e),
                source=source_path,
                destination=destination_path,
                provider=provider
            )
            raise 