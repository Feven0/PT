"""Test infrastructure components."""
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from aiohttp import ClientError

from core.di.container import ContainerError
from .base import BaseTest

class TestInfrastructureComponents(BaseTest):
    """Test infrastructure component initialization and behavior."""
    
    @pytest.mark.asyncio
    async def test_strapi_client_initialization(self, container):
        """Test Strapi client initialization and connection."""
        # Test successful initialization
        assert container.strapi_client.is_initialized
        assert container.strapi_client._session is not None
        
        # Verify metrics were recorded
        with self.assert_metrics(container, {
            "strapi_client_operations_total": 1,
            "strapi_client_connection_status": 1
        }):
            await container.strapi_client.check_health()
    
    @pytest.mark.asyncio
    async def test_strapi_client_resilience(self, container):
        """Test Strapi client resilience mechanisms."""
        client = container.strapi_client
        
        # Test retry mechanism
        with patch.object(client._session, 'get', side_effect=[
            ClientError(),  # First attempt fails
            MagicMock(status=200)  # Second attempt succeeds
        ]):
            with self.assert_metrics(container, {
                "strapi_client_retry_attempts": 1,
                "strapi_client_operations_total": 1
            }):
                await client.validate_connection()
        
        # Test circuit breaker
        with patch.object(client._session, 'get', side_effect=ClientError):
            for _ in range(client.circuit_breaker.failure_threshold):
                with pytest.raises(ClientError):
                    await client.validate_connection()
            
            # Circuit should be open now
            with self.assert_metrics(container, {
                "strapi_client_circuit_breaker_state": 0  # 0 = open
            }):
                with pytest.raises(CircuitBreakerError):
                    await client.validate_connection()
    
    @pytest.mark.asyncio
    async def test_weaviate_client_initialization(self, container):
        """Test Weaviate client initialization and connection."""
        assert container.weaviate_client.is_initialized
        
        # Test schema validation
        with self.assert_metrics(container, {
            "weaviate_client_operations_total": 1
        }):
            await container.weaviate_client.validate_schema()
    
    @pytest.mark.asyncio
    async def test_storage_client_providers(self, container):
        """Test storage client provider management."""
        storage = container.storage_client
        
        # Test provider registration
        assert "s3" in storage._providers
        assert "gdrive" in storage._providers
        
        # Test provider operations
        test_data = b"test data"
        test_key = "test/file.txt"
        
        # Test write through all providers
        await storage.write(test_key, test_data)
        
        # Verify data in each provider
        for provider in storage._providers.values():
            data = await provider.read(test_key)
            assert data == test_data
    
    @pytest.mark.asyncio
    async def test_infrastructure_error_handling(self, container):
        """Test infrastructure error handling and recovery."""
        # Test connection loss handling
        with patch('aiohttp.ClientSession.get', side_effect=ClientError):
            with self.assert_logs([
                "connection_error",
                "retry_attempt",
                "circuit_breaker_open"
            ], level=logging.ERROR):
                with pytest.raises(ContainerError):
                    await container.strapi_client.validate_connection()
        
        # Test recovery after errors
        await asyncio.sleep(container.strapi_client.circuit_breaker.reset_timeout)
        
        with self.assert_metrics(container, {
            "strapi_client_circuit_breaker_state": 1,  # 1 = closed
            "strapi_client_connection_status": 1
        }):
            await container.strapi_client.validate_connection()
    
    @pytest.mark.asyncio
    async def test_infrastructure_health_checks(self, container):
        """Test infrastructure component health checks."""
        components = [
            "strapi_client",
            "weaviate_client",
            "storage_client"
        ]
        
        # Test individual health checks
        for component in components:
            await self.assert_health_check(container, component)
        
        # Test metrics after health checks
        metrics = self.get_component_metrics(container, "health_check")
        assert metrics["health_check_total"] == len(components)
        assert metrics["health_check_success"] == len(components)
    
    @pytest.mark.asyncio
    async def test_infrastructure_cleanup(self, container):
        """Test proper cleanup of infrastructure resources."""
        # Create some test resources
        test_data = b"cleanup test"
        test_keys = [f"test/cleanup_{i}.txt" for i in range(3)]
        
        for key in test_keys:
            await container.storage_client.write(key, test_data)
        
        # Verify cleanup
        with self.assert_metrics(container, {
            "storage_client_cleanup_operations": len(test_keys)
        }):
            await container.cleanup()
        
        # Verify resources are cleaned up
        for key in test_keys:
            with pytest.raises(KeyError):
                await container.storage_client.read(key) 