"""LLM metrics repository implementation."""
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone, timedelta

from weaviate.classes.query import Filter

from core.types.base import ComponentNames as CN
from core.base import BaseRepository
from core.config import AppConfig
from core.logging import BackendLogger
from core.cache.manager import CacheManager
from core.alert.manager import AlertManager
from core.telemetry.metrics import MetricsManager
from core.types.metrics import MetricType
from infrastructure.weaviate.client import WeaviateInfrastructureClient
from infrastructure.weaviate.dynamic import WeaviateDynamicService
from infrastructure.strapi.client import StrapiClient
from infrastructure.strapi.services import StrapiServiceFactory
from infrastructure.weaviate.schemas import get_schema
from core.types.components import HealthStatus

class LLMMetricsError(Exception):
    """Base LLM metrics error."""
    pass

class LLMMetricsRepository(BaseRepository):
    """Repository for managing LLM metrics."""

    REQUIRED_CONFIG = {
        'batch_size': int,
        'max_retries': int,
        'retention_days': int
    }

    def __init__(
        self,
        name: str,
        config: AppConfig,
        metrics: Optional[MetricsManager] = None,
        cache: Optional[CacheManager] = None,
        weaviate_client: Optional[WeaviateInfrastructureClient] = None,
        strapi_client: Optional[StrapiClient] = None,
        alert_manager: Optional[AlertManager] = None,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize LLM metrics repository.
        
        Args:
            name: Repository name
            config: Application configuration
            metrics: Optional metrics manager
            cache: Optional cache manager
            weaviate_client: Optional Weaviate client
            alert_manager: Optional alert manager
            logger: Optional logger
            dependencies: Optional set of dependency names
        """
        required_deps = {CN.metrics_manager, CN.weaviate_client}
        if dependencies:
            required_deps.update(dependencies)
            
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            cache=cache,
            logger=logger,
            dependencies=required_deps,
            required_config=self.REQUIRED_CONFIG
        )
        
        self.alert_manager = alert_manager
        self.cache = cache

        # Store clients
        self.weaviate_client = weaviate_client
        self.strapi_client = strapi_client

        self.weaviate_service = None
        if weaviate_client:
            self.weaviate_service = WeaviateDynamicService(
                client=weaviate_client,
                schema=get_schema("LLMMetrics"),
                logger=self.logger
            )
            
        # Get validated repository config
        self._repository_config = self._config
        
        # Initialize settings from config
        self._batch_size = self._repository_config.get('batch_size', 100)
        self._max_retries = self._repository_config.get('max_retries', 3)
        self._retention_days = self._repository_config.get('retention_days', 30)
        
        # Initialize metrics if available
        if metrics:
            self._register_metrics()

        # Update health status with config details
        self.update_health_details({
            "config": {
                "batch_size": self._batch_size,
                "max_retries": self._max_retries,
                "retention_days": self._retention_days
            }
        })

    async def initialize(self) -> None:
        """Initialize repository."""
        if self.weaviate_service:
            await self.weaviate_service.initialize()

    async def add_metrics(
        self,
        metrics_data: Dict[str, Any],
        vector: Optional[List[float]] = None
    ) -> str:
        """Add LLM metrics.
        
        Args:
            metrics_data: Metrics data
            vector: Optional vector
            
        Returns:
            Metrics UUID
        """
        try:
            # Add timestamp if not present
            if "timestamp" not in metrics_data:
                metrics_data["timestamp"] = datetime.now(timezone.utc).isoformat()
                
            return await self.weaviate_service.add_object(
                data_object=metrics_data,
                vector=vector
            )
        except Exception as e:
            self.logger.error(f"Failed to add metrics: {str(e)}")
            raise LLMMetricsError(f"Failed to add metrics: {str(e)}")

    async def get_metrics(
        self,
        uuid: str,
        with_vector: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Get metrics by UUID.
        
        Args:
            uuid: Metrics UUID
            with_vector: Whether to include vector
            
        Returns:
            Metrics data if found
        """
        try:
            return await self.weaviate_service.get_object(
                uuid=uuid,
                with_vector=with_vector
            )
        except Exception as e:
            self.logger.error(f"Failed to get metrics {uuid}: {str(e)}")
            raise LLMMetricsError(f"Failed to get metrics {uuid}: {str(e)}")

    async def update_metrics(
        self,
        uuid: str,
        metrics_data: Dict[str, Any],
        vector: Optional[List[float]] = None
    ) -> None:
        """Update metrics.
        
        Args:
            uuid: Metrics UUID
            metrics_data: Updated metrics data
            vector: Optional updated vector
        """
        try:
            await self.weaviate_service.update_object(
                uuid=uuid,
                data_object=metrics_data,
                vector=vector
            )
        except Exception as e:
            self.logger.error(f"Failed to update metrics {uuid}: {str(e)}")
            raise LLMMetricsError(f"Failed to update metrics {uuid}: {str(e)}")

    async def delete_metrics(self, uuid: str) -> None:
        """Delete metrics.
        
        Args:
            uuid: Metrics UUID
        """
        try:
            await self.weaviate_service.delete_object(uuid)
        except Exception as e:
            self.logger.error(f"Failed to delete metrics {uuid}: {str(e)}")
            raise LLMMetricsError(f"Failed to delete metrics {uuid}: {str(e)}")

    async def query_metrics(
        self,
        vector: Optional[List[float]] = None,
        near_text: Optional[str] = None,
        where_filter: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
        with_vector: bool = False
    ) -> List[Dict[str, Any]]:
        """Query metrics.
        
        Args:
            vector: Optional query vector
            near_text: Optional text query
            where_filter: Optional filter
            limit: Maximum number of results
            offset: Result offset
            with_vector: Whether to include vectors
            
        Returns:
            List of matching metrics
        """
        try:
            # Convert dict filter to Filter object if provided
            filter_obj = None
            if where_filter:
                filter_obj = Filter()
                for field, value in where_filter.items():
                    if isinstance(value, dict):
                        operator = value.get("operator", "equal")
                        filter_value = value.get("value")
                        if operator == "equal":
                            filter_obj = filter_obj.by_property(field).equal(filter_value)
                        elif operator == "greater_than":
                            filter_obj = filter_obj.by_property(field).greater_than(filter_value)
                        elif operator == "less_than":
                            filter_obj = filter_obj.by_property(field).less_than(filter_value)
                    else:
                        filter_obj = filter_obj.by_property(field).equal(value)
                        
            return await self.weaviate_service.query(
                vector=vector,
                near_text=near_text,
                where_filter=filter_obj,
                limit=limit,
                offset=offset,
                with_vector=with_vector
            )
        except Exception as e:
            self.logger.error(f"Failed to query metrics: {str(e)}")
            raise LLMMetricsError(f"Failed to query metrics: {str(e)}")

    async def batch_add_metrics(
        self,
        metrics_list: List[Dict[str, Any]],
        vectors: Optional[List[List[float]]] = None,
        batch_size: Optional[int] = None
    ) -> List[str]:
        """Add metrics in batch.
        
        Args:
            metrics_list: List of metrics data
            vectors: Optional list of vectors
            batch_size: Optional batch size override
            
        Returns:
            List of metrics UUIDs
        """
        try:
            # Add timestamps if not present
            now = datetime.now(timezone.utc).isoformat()
            for metrics in metrics_list:
                if "timestamp" not in metrics:
                    metrics["timestamp"] = now
                    
            return await self.weaviate_service.batch_add_objects(
                objects=metrics_list,
                vectors=vectors,
                batch_size=batch_size or self._batch_size
            )
        except Exception as e:
            self.logger.error(f"Failed to batch add metrics: {str(e)}")
            raise LLMMetricsError(f"Failed to batch add metrics: {str(e)}")

    async def cleanup_old_metrics(self) -> None:
        """Delete metrics older than retention period."""
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=self._retention_days)
            cutoff_str = cutoff.isoformat()
            
            # Query for old metrics
            filter_obj = Filter().by_property("timestamp").less_than(cutoff_str)
            old_metrics = await self.weaviate_service.query(
                where_filter=filter_obj,
                limit=1000  # Process in chunks
            )
            
            if old_metrics:
                # Extract UUIDs
                uuids = [m["uuid"] for m in old_metrics]
                
                # Delete in batch
                await self.weaviate_service.batch_delete_objects(
                    uuids=uuids,
                    batch_size=self._batch_size
                )
                
                self.logger.info(f"Deleted {len(uuids)} old metrics records")
        except Exception as e:
            self.logger.error(f"Failed to cleanup old metrics: {str(e)}")
            raise LLMMetricsError(f"Failed to cleanup old metrics: {str(e)}")

    async def get_metrics_summary(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get metrics summary.
        
        Args:
            start_time: Optional start time filter
            end_time: Optional end time filter
            provider: Optional provider filter
            model: Optional model filter
            
        Returns:
            Metrics summary
        """
        try:
            # Build filter
            filter_obj = Filter()
            
            if start_time:
                filter_obj = filter_obj.by_property("timestamp").greater_than(start_time.isoformat())
            if end_time:
                filter_obj = filter_obj.by_property("timestamp").less_than(end_time.isoformat())
            if provider:
                filter_obj = filter_obj.by_property("provider").equal(provider)
            if model:
                filter_obj = filter_obj.by_property("model").equal(model)
                
            # Query metrics
            metrics = await self.weaviate_service.query(
                where_filter=filter_obj,
                limit=10000  # Get all matching metrics
            )
            
            # Calculate summary
            summary = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_tokens": 0,
                "average_latency": 0.0,
                "total_cost": 0.0
            }
            
            if metrics:
                for m in metrics:
                    summary["total_requests"] += m.get("total_requests", 0)
                    summary["successful_requests"] += m.get("successful_requests", 0)
                    summary["failed_requests"] += m.get("failed_requests", 0)
                    summary["total_tokens"] += m.get("total_tokens", 0)
                    summary["total_cost"] += m.get("total_cost", 0.0)
                    
                # Calculate average latency
                total_latency = sum(m.get("average_latency", 0.0) for m in metrics)
                summary["average_latency"] = total_latency / len(metrics) if metrics else 0.0
                
            return summary
        except Exception as e:
            self.logger.error(f"Failed to get metrics summary: {str(e)}")
            raise LLMMetricsError(f"Failed to get metrics summary: {str(e)}")

    def _register_metrics(self) -> None:
        """Register repository metrics."""
        self.metrics.register_metric(
            f"{self.name}_operations_total",
            MetricType.COUNTER,
            "Total number of repository operations",
            labels={"operation": "", "status": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_errors_total",
            MetricType.COUNTER,
            "Total number of repository errors",
            labels={"operation": "", "error_type": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_operation_duration_seconds",
            MetricType.HISTOGRAM,
            "Duration of repository operations",
            labels={"operation": ""}
        ) 

    async def check_health(self) -> Dict[str, Any]:
        """Check repository health.
        
        Returns:
            Health check results
        """
        health_status = await super().check_health()
        results = health_status.details
        
        # Check Weaviate connection
        try:
            weaviate_health = await self.weaviate_client.get_health()
            results.update({'weaviate_status': HealthStatus.HEALTHY})
        except Exception as e:
            results.update({'weaviate_status': HealthStatus.UNHEALTHY})
            
        return results
