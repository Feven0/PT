"""Weaviate client implementation."""
from typing import Dict, Any, Optional, Set, List, Union
from datetime import datetime
import asyncio
from uuid import UUID
from contextlib import asynccontextmanager

import weaviate
from weaviate.connect import ConnectionParams
from weaviate.classes.init import AdditionalConfig, Timeout, Auth
from weaviate import WeaviateAsyncClient
from weaviate.exceptions import WeaviateBaseError as WeaviateError
from weaviate.collections import Collection

from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.config import AppConfig
from core.base.infrastructure import BaseInfrastructureClient
from core.base.registry import LifecycleRegistry
from core.resilience.retry import RetryManager
from core.resilience.circuit_breaker import CircuitBreaker
from core.resilience.rate_limiter import RateLimiter
from core.alert.manager import AlertManager
from core.cache.manager import CacheManager
from core.types.metrics import MetricType
from core.telemetry.decorators import track_component_operation


class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass


class WeaviateInfrastructureClient(BaseInfrastructureClient):
    """Weaviate infrastructure client."""

    REQUIRED_CONFIG = {
        'api_url': str,
        'api_key': str,
        'batch_size': int,
        'timeout': float
    }

    def __init__(
        self,
        name: str,
        config: AppConfig,
        metrics: Optional[MetricsManager] = None,
        retry: Optional[RetryManager] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        rate_limiter: Optional[RateLimiter] = None,   
        alert_manager: Optional[AlertManager] = None,
        cache: Optional[CacheManager] = None,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize Weaviate client.
        
        Args:
            name: Client name
            config: Application configuration containing:
                - api_url: Weaviate server URL
                - api_key: Authentication API key
                - version: API version (default: v4)
                - timeout: Dict with connect_timeout and read_timeout in seconds
            metrics: Optional metrics manager
            retry: Optional retry manager
            circuit_breaker: Optional circuit breaker
            rate_limiter: Optional rate limiter
            alert_manager: Optional alert manager
            cache: Optional cache manager
            logger: Optional logger instance
            dependencies: Optional set of dependency names
        """
        super().__init__(name, 
                         config=config, 
                         metrics=metrics, 
                         logger=logger or BackendLogger("weaviate"),
                         dependencies=dependencies or set())

        self._client = None
        self._client_config = self._get_client_config()
        
        self._retry = retry
        self._circuit_breaker = circuit_breaker
        self._rate_limiter = rate_limiter
        self._alert_manager = alert_manager
        self._cache = cache

        # Register metrics if available
        if self.metrics:
            self._register_metrics()

    def _get_client_config(self) -> Dict[str, Any]:
        """Extract and validate client configuration.
        
        Returns:
            Dict containing validated configuration with defaults
        """
        try:
            # Parse URL components
            api_url = self._config.get('api_url', '')
            if not api_url.startswith(('http://', 'https://')):
                api_url = f"https://{api_url}"
                
            # Extract host and port
            from urllib.parse import urlparse
            parsed_url = urlparse(api_url)
            host = parsed_url.hostname or ''
            port = str(parsed_url.port or 443)
            scheme = parsed_url.scheme or 'https'
            
            config = {
                'api_url': host,  # Just the hostname
                'api_key': self._config.get('api_key', ''),
                'batch_size': self._config.get('batch_size', 100),
                'vector_index_type': self._config.get('vector_index_type', 'hnsw'),
                'vector_cache_size': self._config.get('vector_cache_size', 100000),
                'timeout': self._config.get('timeout', 30.0),
                'http_port': port,
                'http_secure': scheme == 'https',
                'grpc_port': str(int(port) + 1),  # gRPC port is typically HTTP port + 1
                'grpc_secure': scheme == 'https'
            }
            
            # Validate fields and log warnings for missing or invalid types
            for field, field_type in self.REQUIRED_CONFIG.items():
                if not config.get(field):
                    if self.logger:
                        self.logger.warning(
                            f"Missing config field: {field}, using default value",
                            context="weaviate_client",
                            field=field,
                            default_value=config[field]
                        )
                elif not isinstance(config.get(field), field_type):
                    if self.logger:
                        self.logger.warning(
                            f"Invalid type for config field {field}. Expected {field_type}, got {type(config[field])}. Attempting conversion.",
                            context="weaviate_client",
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
                                context="weaviate_client",
                                field=field,
                                value=config.get(field)
                            )
                            
            # Update health status with config details
            self._health_status.update(details={
                'api_url': config['api_url'],
                'batch_size': config['batch_size'],
                'vector_index_type': config['vector_index_type'],
                'vector_cache_size': config['vector_cache_size'],
                'timeout': config['timeout']
            })
            
            return config
            
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"Failed to get client config: {str(e)}",
                    context="weaviate_client",
                    error=str(e)
                )
            # Return default configuration
            return {
                'api_url': '',
                'api_key': '',
                'batch_size': 100,
                'vector_index_type': 'hnsw',
                'vector_cache_size': 100000,
                'timeout': 30.0,
                'http_port': '443',
                'http_secure': True,
                'grpc_port': '444',
                'grpc_secure': True
            }

    def _register_metrics(self) -> None:
        """Register infrastructure metrics."""
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
        
        # Connection Metrics
        self.metrics.register_metric(
            f"{self.name}_connection_errors_total",
            MetricType.COUNTER,
            f"Total number of connection errors in {self.name}",
            labels={"error_type": ""}
        )
        
        self.metrics.register_metric(
            f"{self.name}_connection_status",
            MetricType.GAUGE,
            f"Current connection status in {self.name}",
            labels={"status": ""}
        )
        
        # Performance Metrics
        self.metrics.register_metric(
            f"{self.name}_operation_duration_seconds",
            MetricType.HISTOGRAM,
            f"Duration of operations in {self.name}",
            labels={"operation": "", "status": ""}
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
        """Initialize Weaviate client."""
        try:
            # Initialize client with async connection method
            self._client = weaviate.WeaviateAsyncClient(
                connection_params=ConnectionParams.from_params(
                    http_host=self._client_config['api_url'],
                    http_port=self._client_config['http_port'],
                    http_secure=self._client_config['http_secure'],
                    grpc_host=self._client_config['api_url'],
                    grpc_port=self._client_config['grpc_port'],
                    grpc_secure=self._client_config['grpc_secure'],
                ),
                auth_client_secret=Auth.api_key(self._client_config['api_key']),
                additional_headers={
                    "X-Client-Name": self.name,
                    "X-Client-Version": "v4"
                },
                additional_config=AdditionalConfig(
                    timeout=Timeout(
                        init=self._client_config['timeout'],
                        query=self._client_config['timeout'] * 2,
                        insert=self._client_config['timeout'] * 4
                    )
                ),
                skip_init_checks=False  # Enable init checks for better error detection
            )
            
            # Connect to the server
            await self._client.connect()
            
            # Validate connection
            await self._validate_connection()
            
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "initialize", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_connection_status",
                    1,
                    labels={"status": "connected"}
                )
                
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_connection_errors_total",
                    1,
                    labels={"error_type": type(e).__name__}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "initialize", "status": "error"}
                )
                self.metrics.record(
                    f"{self.name}_connection_status",
                    0,
                    labels={"status": "disconnected"}
                )
            raise

    @track_component_operation("start")
    async def _start_impl(self) -> None:
        """Start Weaviate client."""
        try:
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
        """Stop Weaviate client."""
        try:
            if self._client:
                await self._client.close()
                self._client = None
                
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": "stop", "status": "success"}
                )
                self.metrics.record(
                    f"{self.name}_connection_status",
                    0,
                    labels={"status": "disconnected"}
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

    async def _validate_connection(self) -> None:
        """Validate Weaviate connection.
        
        Raises:
            WeaviateError: If connection validation fails
        """
        try:
            # Check if client is ready
            if not await self._client.is_ready():
                raise WeaviateError("Weaviate client not ready")
                
            # Check if client is connected
            if not self._client.is_connected():
                raise WeaviateError("Weaviate client not connected")
                
            # Verify schema access by attempting to get collections
            try:
                # Try a basic operation to verify connection
                await self._client.collections.exists("test")
            except Exception as e:
                raise WeaviateError(f"Failed to verify schema access: {str(e)}")
                
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_connection_status",
                    1,
                    labels={"status": "healthy"}
                )
                
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_connection_errors_total",
                    1,
                    labels={"error_type": type(e).__name__}
                )
                self.metrics.record(
                    f"{self.name}_connection_status",
                    0,
                    labels={"status": "unhealthy"}
                )
            raise WeaviateError(f"Connection validation failed: {str(e)}")

    async def get_health(self) -> Dict[str, Any]:
        """Get client health status.
        
        Returns:
            Health status details
        """
        health = await super().get_health()
        
        try:
            # Add client-specific health details
            if self._client:
                ready = await self._client.is_ready()
                health.update({
                    "ready": ready,
                    "api_url": self._client_config['api_url'],
                    "metrics": self.metrics.get_all() if self.metrics else {}
                })
                
        except Exception as e:
            health.update({
                "error": str(e)
            })
            
        return health 


    async def execute_operation(self, operation: str, *args, **kwargs) -> Any:
        """Execute Weaviate operation with resilience patterns.
        
        Args:
            operation: Operation name
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Operation result
            
        Raises:
            WeaviateError: If operation fails
        """
        return await self._execute_with_resilience(
            operation,
            self._execute_operation,
            operation,
            *args,
            **kwargs
        )

    async def _execute_operation(self, operation: str, *args, **kwargs) -> Any:
        """Execute Weaviate operation.
        
        Args:
            operation: Operation name
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Operation result
            
        Raises:
            WeaviateError: If operation fails
        """
        try:
            if not self._client:
                raise WeaviateError("Client not initialized")
            
            # Map operations to implementation methods
            operation_map = {
                "create_class": self._do_create_class,
                "delete_class": self._do_delete_class,
                "get_class": self._do_get_class,
                "add_object": self._do_add_object,
                "get_object": self._do_get_object,
                "update_object": self._do_update_object,
                "delete_object": self._do_delete_object,
                "query": self._do_query,
                "batch_add_objects": self._do_batch_add_objects,
                "batch_delete_objects": self._do_batch_delete_objects
            }
            
            # Get implementation method
            impl_method = operation_map.get(operation)
            if not impl_method:
                raise WeaviateError(f"Unknown operation: {operation}")
            
            # Execute operation implementation
            result = await impl_method(*args, **kwargs)
            
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "status": "success"}
                )
            
            return result
            
        except Exception as e:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_errors_total",
                    1,
                    labels={"error_type": type(e).__name__, "operation": operation}
                )
                self.metrics.record(
                    f"{self.name}_operations_total",
                    1,
                    labels={"operation": operation, "status": "error"}
                )
            
            if isinstance(e, WeaviateError):
                raise
            
            raise WeaviateError(f"Operation {operation} failed: {str(e)}") from e

    @asynccontextmanager
    async def _get_collection(self, collection_name: str) -> Collection:
        """Get a collection with proper async context management.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection object
            
        Raises:
            WeaviateError: If collection access fails
        """
        try:
            # Note: get() is synchronous
            collection = self._client.collections.get(collection_name)
            yield collection
        except Exception as e:
            raise WeaviateError(f"Failed to access collection {collection_name}: {str(e)}")
        
    async def _do_query(
        self,
        class_name: str,
        vector: Optional[List[float]] = None,
        near_text: Optional[str] = None,
        where_filter: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
        with_vector: bool = False
    ) -> List[Dict[str, Any]]:
        """Query implementation."""
        try:
            collection = self._client.collections.get(class_name)
            
            # Choose query type based on parameters
            if vector is not None:
                result = await collection.query.near_vector(
                    near_vector=vector,
                    filters=where_filter,
                    limit=limit,
                    offset=offset,
                    include_vector=with_vector
                )
            elif near_text is not None:
                result = await collection.query.near_text(
                    query=near_text,
                    filters=where_filter,
                    limit=limit,
                    offset=offset,
                    include_vector=with_vector
                )
            else:
                result = await collection.query.fetch_objects(
                    filters=where_filter,
                    limit=limit,
                    offset=offset,
                    include_vector=with_vector
                )
                
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_query_results_total",
                    len(result.objects),
                    labels={"operation": "query"}
                )
                
            return result.objects
            
        except Exception as e:
            raise WeaviateError(f"Query failed for {class_name}: {str(e)}") from e

    async def _do_add_object(
        self,
        class_name: str,
        data_object: Dict[str, Any],
        vector: Optional[List[float]] = None,
        uuid: Optional[Union[str, UUID]] = None
    ) -> str:
        """Add object implementation."""
        try:
            collection = self._client.collections.get(class_name)
            return await collection.data.insert(
                properties=data_object,
                vector=vector,
                uuid=str(uuid) if uuid else None
            )
        except Exception as e:
            raise WeaviateError(f"Failed to add object to {class_name}: {str(e)}") from e

    async def _do_get_object(
        self,
        class_name: str,
        uuid: Union[str, UUID],
        with_vector: bool = False
    ) -> Dict[str, Any]:
        """Get object implementation."""
        try:
            collection = self._client.collections.get(class_name)
            return await collection.data.get_by_id(
                uuid=str(uuid),
                include_vector=with_vector
            )
        except Exception as e:
            raise WeaviateError(f"Failed to get object {uuid} from {class_name}: {str(e)}") from e

    async def _do_update_object(
        self,
        class_name: str,
        uuid: Union[str, UUID],
        data_object: Dict[str, Any],
        vector: Optional[List[float]] = None
    ) -> None:
        """Update object implementation."""
        try:
            collection = self._client.collections.get(class_name)
            await collection.data.update(
                uuid=str(uuid),
                properties=data_object,
                vector=vector
            )
        except Exception as e:
            raise WeaviateError(f"Failed to update object {uuid} in {class_name}: {str(e)}") from e

    async def _do_delete_object(
        self,
        class_name: str,
        uuid: Union[str, UUID]
    ) -> None:
        """Delete object implementation."""
        try:
            collection = self._client.collections.get(class_name)
            await collection.data.delete_by_id(str(uuid))
        except Exception as e:
            raise WeaviateError(f"Failed to delete object {uuid} from {class_name}: {str(e)}") from e

    async def _do_batch_add_objects(
        self,
        class_name: str,
        objects: List[Dict[str, Any]],
        vectors: Optional[List[List[float]]] = None,
        uuids: Optional[List[Union[str, UUID]]] = None,
        batch_size: int = 100
    ) -> List[str]:
        """Batch add objects implementation."""
        try:
            collection = self._client.collections.get(class_name)
            object_uuids = []
            
            async with collection.batch.dynamic() as batch:
                batch.batch_size = batch_size
                
                for i, obj in enumerate(objects):
                    uuid = str(uuids[i]) if uuids and i < len(uuids) else None
                    vector = vectors[i] if vectors and i < len(vectors) else None
                    
                    uuid = await batch.add_object(
                        properties=obj,
                        vector=vector,
                        uuid=uuid
                    )
                    object_uuids.append(uuid)
                    
            # Check for failed objects
            if batch.failed_objects:
                self.logger.warning(
                    f"Failed to add {len(batch.failed_objects)} objects in batch"
                )
                
            return object_uuids
            
        except Exception as e:
            raise WeaviateError(f"Failed to batch add objects to {class_name}: {str(e)}") from e

    async def _do_batch_delete_objects(
        self,
        class_name: str,
        uuids: List[Union[str, UUID]],
        batch_size: int = 100
    ) -> None:
        """Batch delete objects implementation."""
        try:
            collection = self._client.collections.get(class_name)
            
            # Convert UUIDs to strings
            uuid_strings = [str(uuid) for uuid in uuids]
            
            # Delete in batches
            for i in range(0, len(uuid_strings), batch_size):
                batch = uuid_strings[i:i + batch_size]
                await collection.data.delete_many(
                    uuids=batch
                )
        except Exception as e:
            raise WeaviateError(f"Failed to batch delete objects from {class_name}: {str(e)}") from e


    async def _do_create_class(
        self,
        class_name: str,
        class_config: Dict[str, Any]
    ) -> None:
        """Create Weaviate class implementation."""
        try:
            # Ensure properties is a list of Property objects
            properties = class_config.get("properties", [])
            if isinstance(properties, dict):
                properties = [Property(**prop) for prop in properties]
            elif isinstance(properties, list) and properties and isinstance(properties[0], dict):
                properties = [Property(**prop) for prop in properties]

            # Add required configuration
            config = {
                "name": class_name,
                "properties": properties,
                "description": class_config.get("description", f"Collection for {class_name}"),
            }
            for key, value in class_config.items():
                if key not in config:
                    config[key] = value

            await self._client.collections.create(**config)
        except Exception as e:
            raise WeaviateError(f"Failed to create class {class_name}: {str(e)}")

    async def _do_get_class(
        self,
        class_name: str
    ) -> Dict[str, Any]:
        """Get Weaviate class implementation."""
        try:
            collection = self._client.collections.get(class_name)
            return await collection.exists()
        except Exception as e:
            raise WeaviateError(f"Failed to get class {class_name}: {str(e)}") from e

    async def _do_delete_class(
        self,
        class_name: str
    ) -> None:
        """Delete Weaviate class implementation."""
        try:
            await self._client.collections.delete(class_name)
        except Exception as e:
            raise WeaviateError(f"Failed to delete class {class_name}: {str(e)}") from e

    async def create_class(
        self,
        class_name: str,
        class_config: Dict[str, Any]
    ) -> None:
        """Create Weaviate class.
        
        Args:
            class_name: Class name
            class_config: Class configuration
            
        Raises:
            WeaviateError: If creation fails
        """
        await self.execute_operation(
            "create_class",
            class_name,
            class_config
        )

    async def delete_class(self, class_name: str) -> None:
        """Delete Weaviate class.
        
        Args:
            class_name: Class name
            
        Raises:
            WeaviateError: If deletion fails
        """
        await self.execute_operation(
            "delete_class", 
            class_name
        )

    async def add_object(
        self,
        class_name: str,
        data_object: Dict[str, Any],
        vector: Optional[List[float]] = None,
        uuid: Optional[Union[str, UUID]] = None
    ) -> str:
        """Add object to Weaviate.
        
        Args:
            class_name: Class name
            data_object: Object data
            vector: Optional vector
            uuid: Optional UUID
            
        Returns:
            Object UUID
            
        Raises:
            WeaviateError: If add fails
        """
        return await self.execute_operation(
            "add_object",
            class_name,
            data_object,
            vector=vector,
            uuid=uuid
        )

    async def get_object(
        self,
        class_name: str,
        uuid: Union[str, UUID],
        with_vector: bool = False
    ) -> Dict[str, Any]:
        """Get object from Weaviate.
        
        Args:
            class_name: Class name
            uuid: Object UUID
            with_vector: Include vector in response
            
        Returns:
            Object data
            
        Raises:
            WeaviateError: If get fails
        """
        return await self.execute_operation(
            "get_object",
            class_name,
            uuid,
            with_vector=with_vector
        )

    async def update_object(
        self,
        class_name: str,
        uuid: Union[str, UUID],
        data_object: Dict[str, Any],
        vector: Optional[List[float]] = None
    ) -> None:
        """Update object in Weaviate.
        
        Args:
            class_name: Class name
            uuid: Object UUID
            data_object: Updated object data
            vector: Optional updated vector
            
        Raises:
            WeaviateError: If update fails
        """
        await self.execute_operation(
            "update_object",
            class_name,
            uuid,
            data_object,
            vector=vector
        )

    async def delete_object(
        self,
        class_name: str,
        uuid: Union[str, UUID]
    ) -> None:
        """Delete object from Weaviate.
        
        Args:
            class_name: Class name
            uuid: Object UUID
            
        Raises:
            WeaviateError: If delete fails
        """
        await self.execute_operation(
            "delete_object",
            class_name,
            uuid
        )

    async def query(
        self,
        class_name: str,
        vector: Optional[List[float]] = None,
        near_text: Optional[str] = None,
        where_filter: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
        with_vector: bool = False
    ) -> List[Dict[str, Any]]:
        """Query objects in Weaviate.
        
        Args:
            class_name: Class name
            vector: Optional vector for similarity search
            near_text: Optional text for semantic search
            where_filter: Optional filter criteria
            limit: Maximum number of results
            offset: Result offset
            with_vector: Include vectors in response
            
        Returns:
            List of matching objects
            
        Raises:
            WeaviateError: If query fails
        """
        return await self.execute_operation(
            "query",
            class_name,
            vector=vector,
            near_text=near_text,
            where_filter=where_filter,
            limit=limit,
            offset=offset,
            with_vector=with_vector
        )

    async def batch_add_objects(
        self,
        class_name: str,
        objects: List[Dict[str, Any]],
        vectors: Optional[List[List[float]]] = None,
        uuids: Optional[List[Union[str, UUID]]] = None,
        batch_size: int = 100
    ) -> List[str]:
        """Add objects in batch to Weaviate.
        
        Args:
            class_name: Class name
            objects: List of objects to add
            vectors: Optional list of vectors
            uuids: Optional list of UUIDs
            batch_size: Batch size
            
        Returns:
            List of object UUIDs
            
        Raises:
            WeaviateError: If batch add fails
        """
        return await self.execute_operation(
            "batch_add_objects",
            class_name,
            objects,
            vectors=vectors,
            uuids=uuids,
            batch_size=batch_size
        )

    async def batch_delete_objects(
        self,
        class_name: str,
        uuids: List[Union[str, UUID]],
        batch_size: int = 100
    ) -> None:
        """Delete objects in batch from Weaviate.
        
        Args:
            class_name: Class name
            uuids: List of UUIDs to delete
            batch_size: Batch size
            
        Raises:
            WeaviateError: If batch delete fails
        """
        await self.execute_operation(
            "batch_delete_objects",
            class_name,
            uuids,
            batch_size=batch_size
        )

    async def _cleanup_impl(self) -> None:
        """Clean up Weaviate client resources."""
        try:
            if self._client:
                await self._client.close()
                self._client = None
                
            if self.logger:
                self.logger.info(
                    "weaviate_client_cleaned_up",
                    client=self.name
                )
                
        except Exception as e:
            if self.logger:
                self.logger.error(
                    "weaviate_cleanup_failed",
                    error=str(e),
                    client=self.name
                )
            raise