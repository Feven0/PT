"""Analysis repository implementation."""
from typing import Optional, Dict, Any, List, Set, Union
from datetime import datetime, timezone
import asyncio
import time
from uuid import UUID, uuid4
from pydantic import Field

from core.types.base import ComponentNames as CN
from core.base.repository import BaseRepository
from core.config.base import AppConfig
from core.cache.manager import CacheManager
from core.alert.manager import AlertManager
from core.telemetry.metrics import MetricsManager
from core.errors.exceptions import AnalysisError, NotFoundError
from infrastructure.strapi.client import StrapiClient
from infrastructure.strapi.services import StrapiServiceFactory
from infrastructure.weaviate.client import WeaviateInfrastructureClient
from infrastructure.weaviate.dynamic import WeaviateDynamicService
from infrastructure.weaviate.schemas import get_schema
from core.types.analysis import AnalysisResult, AnalysisMetric, AnalysisType, AnalysisStatus, QuestionStatus
from domain.models.analysis import SessionAnalysis, QuestionAnalysis
from core.telemetry.decorators import track_component_operation
from core.types.metrics import MetricType
from core.types.model import CoreBaseModel
from core.telemetry.metrics import MetricsManager as CoreMetricsManager
from core.logging import BackendLogger
from core.types.components import HealthStatus


class ConfigError(AnalysisError):
    """Configuration error."""
    pass

class AnalysisNotFoundError(AnalysisError):
    """Error raised when analysis is not found."""
    pass

class AnalysisCreationError(AnalysisError):
    """Error raised when analysis creation fails."""
    pass

class AnalysisUpdateError(AnalysisError):
    """Error raised when analysis update fails."""
    pass

class AnalysisDeletionError(AnalysisError):
    """Error raised when analysis deletion fails."""
    pass

class AnalysisRepository(BaseRepository):
    """Repository for managing interview analysis data."""
    
    
    REQUIRED_CONFIG = {
        'cache_ttl': int,
        'batch_size': int,
        'max_retries': int,
        'vector_dimension': int,
        'similarity_threshold': float
    }

    def __init__(
        self,
        name: str,
        config: AppConfig,
        metrics: Optional[MetricsManager] = None,
        cache: Optional[CacheManager] = None,
        strapi_client: Optional[StrapiClient] = None,
        weaviate_client: Optional[WeaviateInfrastructureClient] = None,
        alert_manager: Optional[AlertManager] = None,     
        logger: Optional[BackendLogger] = None,        
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize analysis repository.
        
        Args:
            name: Repository name
            config: Application configuration
            metrics: Optional metrics manager
            dependencies: Optional set of dependency names
            weaviate_client: Weaviate client instance
        """
        # Initialize base repository
        required_deps = {CN.metrics_manager, 
                         CN.weaviate_client}
        if dependencies:
            required_deps.update(dependencies)
            
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            dependencies=required_deps,
            required_config=self.REQUIRED_CONFIG
        )
        
        # Store clients
        self.cache = cache
        self.strapi_client = strapi_client
        self.weaviate_client = weaviate_client
        self.alert_manager = alert_manager
        
        # Initialize services
        self.weaviate_service = WeaviateDynamicService(
            client=weaviate_client,
            schema=get_schema("Analysis"),
            logger=self.logger
        )
        
        
        # Initialize analysis repository settings from validated config
        self._cache_ttl = self._repository_config.get('cache_ttl', 3600)
        self._batch_size = self._repository_config.get('batch_size', 100)
        self._max_retries = self._repository_config.get('max_retries', 3)
        self._vector_dimension = self._repository_config.get('vector_dimension', 1536)
        self._similarity_threshold = self._repository_config.get('similarity_threshold', 0.7)
        
        # Initialize resilience components
        if metrics:
            self._register_metrics()
            
        
        # Update health status with config details
        self.update_health_details({
            "config": {
                "cache_ttl": self._cache_ttl,
                "batch_size": self._batch_size,
                "max_retries": self._max_retries,
                "vector_dimension": self._vector_dimension,
                "similarity_threshold": self._similarity_threshold
            }
        })


    def _register_metrics(self) -> None:
        """Register repository metrics."""
        # Operation Metrics
        self.metrics.register_metric(
            f"{self.name}_operations_total",
            MetricType.COUNTER,
            f"Total number of operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Query Metrics
        self.metrics.register_metric(
            f"{self.name}_query_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of queries in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_query_results_total",
            MetricType.COUNTER,
            f"Total number of query results in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        # Batch Operation Metrics
        self.metrics.register_metric(
            f"{self.name}_batch_operations_total",
            MetricType.COUNTER,
            f"Total number of batch operations in {self.name}",
            labels={"operation": "", "status": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_batch_size",
            MetricType.GAUGE,
            f"Current batch size in {self.name}",
            labels={"operation": ""}
        )
        
        # Error Metrics
        self.metrics.register_metric(
            f"{self.name}_errors_total",
            MetricType.COUNTER,
            f"Total number of errors in {self.name}",
            labels={"error_type": "", "operation": ""}
        )

    @track_component_operation("initialize")
    async def _initialize_impl(self) -> None:
        """Initialize analysis repository."""
        try:
            if self.weaviate_client:
                await self.weaviate_client.initialize()
                
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "initialize", "status": "success"}
                )
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "initialize"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "initialize", "status": "error"}
                )
            raise

    @track_component_operation("start")
    async def _start_impl(self) -> None:
        """Start analysis repository."""
        try:
            if self.weaviate_client:
                await self.weaviate_client.start()
                
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "start", "status": "success"}
                )
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "start"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "start", "status": "error"}
                )
            raise

    @track_component_operation("stop")
    async def _stop_impl(self) -> None:
        """Stop analysis repository."""
        try:
            if self.weaviate_client:
                await self.weaviate_client.stop()
                
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "stop", "status": "success"}
                )
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": "stop"}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "stop", "status": "error"}
                )
            raise
            

    async def store_analysis(self, analysis: AnalysisResult) -> AnalysisResult:
        """Store analysis result.
        
        Args:
            analysis: Analysis result to store
            
        Returns:
            Stored analysis result
            
        Raises:
            AnalysisCreationError: If storage fails
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            # Store in vector database
            self._store_vector(
                collection="analysis_results",
                id=str(analysis.id),
                data=analysis.model_dump()
            )
            
            # Record metrics
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.metrics.record(
                "analysis_storage_duration",
                duration,
                {"analysis_id": str(analysis.id)}
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to store analysis: {str(e)}")
            raise AnalysisCreationError(f"Failed to store analysis: {str(e)}")

    async def get_analysis(self, analysis_id: UUID) -> Optional[AnalysisResult]:
        """Get analysis result.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Analysis result if found, None otherwise
            
        Raises:
            AnalysisError: If retrieval fails
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            # Get from vector database
            data = self._get_vector(
                collection="analysis_results",
                id=str(analysis_id)
            )
            
            if not data:
                return None
            
            # Convert to domain model
            analysis = AnalysisResult(**data)
            
            # Record metrics
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.metrics.record(
                "analysis_retrieval_duration",
                duration,
                {"analysis_id": str(analysis.id)}
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to get analysis: {str(e)}")
            raise AnalysisError(f"Failed to get analysis: {str(e)}")

    async def store_session_analysis(self, analysis: SessionAnalysis) -> SessionAnalysis:
        """Store session analysis.
        
        Args:
            analysis: Session analysis to store
            
        Returns:
            Stored session analysis
            
        Raises:
            AnalysisCreationError: If storage fails
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            # Store in vector database
            self._store_vector(
                collection="session_analyses",
                id=str(analysis.id),
                data=analysis.model_dump()
            )
            
            # Record metrics
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.metrics.record(
                "session_analysis_storage_duration",
                duration,
                {"session_id": str(analysis.session_id)}
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to store session analysis: {str(e)}")
            raise AnalysisCreationError(f"Failed to store session analysis: {str(e)}")

    async def get_session_analysis(self, session_id: UUID) -> Optional[SessionAnalysis]:
        """Get session analysis.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session analysis if found, None otherwise
            
        Raises:
            AnalysisError: If retrieval fails
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            # Get from vector database
            data = self._get_vector(
                collection="session_analyses",
                id=str(session_id)
            )
            
            if not data:
                return None
            
            # Convert to domain model
            analysis = SessionAnalysis(**data)
            
            # Record metrics
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.metrics.record(
                "session_analysis_retrieval_duration",
                duration,
                {"session_id": str(session_id)}
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to get session analysis: {str(e)}")
            raise AnalysisError(f"Failed to get session analysis: {str(e)}")

    def _store_vector(self, collection: str, id: str, data: Dict[str, Any]) -> None:
        """Store data in vector database.
        
        Args:
            collection: Collection name
            id: Document ID
            data: Document data
            
        Raises:
            AnalysisError: If storage fails
        """
        try:
            # Convert datetime objects to ISO format strings
            processed_data = {}
            for key, value in data.items():
                if isinstance(value, datetime):
                    processed_data[key] = value.isoformat()
                elif isinstance(value, UUID):
                    processed_data[key] = str(value)
                elif isinstance(value, (list, dict)):
                    processed_data[key] = self._process_nested_data(value)
                else:
                    processed_data[key] = value
            
            # Store in Weaviate
            self.weaviate_service.add_object(processed_data, uuid=id)
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_vector_storage_total",
                    1,
                    labels={
                        "collection": collection,
                        "status": "success"
                    }
                )
                
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_vector_storage_total",
                    1,
                    labels={
                        "collection": collection,
                        "status": "error",
                        "error": str(e)
                    }
                )
            raise AnalysisError(f"Failed to store vector data: {str(e)}")
    
    def _get_vector(self, collection: str, id: str) -> Optional[Dict[str, Any]]:
        """Get data from vector database.
        
        Args:
            collection: Collection name
            id: Document ID
            
        Returns:
            Document data if found, None otherwise
            
        Raises:
            AnalysisError: If retrieval fails
        """
        try:
            # Get from Weaviate
            data = self.weaviate_service.get_object(id)
            
            if not data:
                return None
            
            # Convert ISO format strings back to datetime objects
            processed_data = {}
            for key, value in data.items():
                if isinstance(value, str):
                    try:
                        # Try to parse as datetime
                        processed_data[key] = datetime.fromisoformat(value)
                    except ValueError:
                        try:
                            # Try to parse as UUID
                            processed_data[key] = UUID(value)
                        except ValueError:
                            processed_data[key] = value
                elif isinstance(value, (list, dict)):
                    processed_data[key] = self._process_nested_data(value, reverse=True)
                else:
                    processed_data[key] = value
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_vector_retrieval_total",
                    1,
                    labels={
                        "collection": collection,
                        "status": "success"
                    }
                )
            
            return processed_data
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_vector_retrieval_total",
                    1,
                    labels={
                        "collection": collection,
                        "status": "error",
                        "error": str(e)
                    }
                )
            raise AnalysisError(f"Failed to get vector data: {str(e)}")
    
    def _process_nested_data(self, data: Union[Dict[str, Any], List[Any]], reverse: bool = False) -> Union[Dict[str, Any], List[Any]]:
        """Process nested data structures for storage/retrieval.
        
        Args:
            data: Data to process
            reverse: Whether to reverse the processing (for retrieval)
            
        Returns:
            Processed data
        """
        if isinstance(data, dict):
            return {
                key: self._process_nested_data(value, reverse)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [
                self._process_nested_data(item, reverse)
                for item in data
            ]
        elif isinstance(data, datetime) and not reverse:
            return data.isoformat()
        elif isinstance(data, str) and reverse:
            try:
                return datetime.fromisoformat(data)
            except ValueError:
                try:
                    return UUID(data)
                except ValueError:
                    return data
        return data

    async def search_analysis(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search analysis data.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching analysis
            
        Raises:
            AnalysisError: If search fails
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            # Search in Weaviate
            results = await self.weaviate_service.query(
                near_text=query,
                limit=limit
            )
            
            # Record metrics
            if self.metrics:
                self.metrics.histogram(
                    "analysis_search_duration_seconds",
                    (datetime.now(timezone.utc) - start_time).total_seconds(),
                    labels={"success": "true"}
                )
                self.metrics.counter(
                    "analysis_search_total",
                    labels={"success": "true"}
                )
                
            return results
            
        except Exception as e:
            if self.metrics:
                self.metrics.counter(
                    "analysis_search_total",
                    labels={"success": "false"}
                )
            self.logger.error(
                "search_analysis_failed",
                error=str(e),
                query=query
            )
            raise AnalysisError(f"Failed to search analysis: {str(e)}")

    async def update_analysis(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> AnalysisResult:
        """Update interview analysis.
        
        Args:
            session_id: Interview session ID
            updates: Fields to update
            
        Returns:
            Updated analysis
            
        Raises:
            NotFoundError: If analysis not found
            AnalysisError: If update fails
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            # Update in Weaviate
            result = await self.weaviate_service.update_by_filter(
                filter_dict={
                    "path": ["session_id"],
                    "operator": "Equal",
                    "valueString": session_id
                },
                data=updates
            )
            
            if not result:
                raise NotFoundError(f"Analysis not found for session: {session_id}")
                
            # Get updated analysis
            analysis = await self.get_analysis(UUID(result["id"]))
            
            # Record metrics
            if self.metrics:
                self.metrics.histogram(
                    "analysis_update_duration_seconds",
                    (datetime.now(timezone.utc) - start_time).total_seconds(),
                    labels={"success": "true"}
                )
                self.metrics.counter(
                    "analysis_update_total",
                    labels={"success": "true"}
                )
                
            return analysis
            
        except NotFoundError:
            if self.metrics:
                self.metrics.counter(
                    "analysis_update_total",
                    labels={
                        "success": "false",
                        "error": "not_found"
                    }
                )
            raise
            
        except Exception as e:
            if self.metrics:
                self.metrics.counter(
                    "analysis_update_total",
                    labels={
                        "success": "false",
                        "error": "other"
                    }
                )
            self.logger.error(
                "update_analysis_failed",
                error=str(e),
                session_id=session_id
            )
            raise AnalysisError(f"Failed to update analysis: {str(e)}")

    async def delete_analysis(
        self,
        session_id: str
    ) -> None:
        """Delete interview analysis.
        
        Args:
            session_id: Interview session ID
            
        Raises:
            NotFoundError: If analysis not found
            AnalysisError: If deletion fails
        """
        try:
            # Delete from Weaviate
            result = await self.weaviate_service.delete_by_filter({
                "path": ["session_id"],
                "operator": "Equal",
                "valueString": session_id
            })
            
            if not result:
                raise NotFoundError(f"Analysis not found for session: {session_id}")
                
            # Record metrics
            if self.metrics:
                self.metrics.counter(
                    "analysis_delete_total",
                    labels={"success": "true"}
                )
                
        except NotFoundError:
            if self.metrics:
                self.metrics.counter(
                    "analysis_delete_total",
                    labels={
                        "success": "false",
                        "error": "not_found"
                    }
                )
            raise
            
        except Exception as e:
            if self.metrics:
                self.metrics.counter(
                    "analysis_delete_total",
                    labels={
                        "success": "false",
                        "error": "other"
                    }
                )
            self.logger.error(
                "delete_analysis_failed",
                error=str(e),
                session_id=session_id
            )
            raise AnalysisError(f"Failed to delete analysis: {str(e)}")

    async def check_health(self) -> Dict[str, Any]:
        """Check repository health.
        
        Returns:
            Health check results
        """
        health_status = await super().check_health()
        results = health_status.details
        
        # Check Weaviate connection
        try:
            await self.weaviate_client.check_health()
            results.update({'weaviate_status': HealthStatus.HEALTHY})
        except Exception as e:
            results.update({'weaviate_status': HealthStatus.UNHEALTHY})
            
        return results
