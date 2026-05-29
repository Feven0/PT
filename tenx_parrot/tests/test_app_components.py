"""Test individual app components."""
import pytest
from fastapi import FastAPI
from typing import AsyncGenerator
from core.di.container import Container
from .helpers import get_test_config

# Step 1: Component-specific fixtures
@pytest.fixture
async def test_container(test_app: FastAPI, mock_config) -> AsyncGenerator[Container, None]:
    """Get the app container and ensure proper cleanup."""
    container = test_app.container
    container.config = mock_config
    try:
        # Initialize if not already initialized
        if not container.is_initialized:
            await container.initialize()
            await container.start()
        yield container
    finally:
        # Cleanup after tests
        await container.stop()
        await container.cleanup()

# Step 2: Test repository layer
@pytest.mark.asyncio
async def test_user_repository(mock_services):
    """Test if user repository is working."""
    repo = mock_services.user_repository
    
    # Check initialization
    assert repo.is_initialized, "Repository should be initialized"
    
    # Test basic operations
    try:
        # Try to get a non-existent user (should return None)
        user = await repo.get("test-user-id")
        assert user is None, "Non-existent user should return None"
    except Exception as e:
        pytest.fail(f"Repository operation failed: {str(e)}")

# Step 3: Test service layer
@pytest.mark.asyncio
async def test_user_service(mock_services):
    """Test if user service is working."""
    service = mock_services.user_service
    
    # Check initialization
    assert service.is_initialized, "Service should be initialized"
    
    # Test service dependencies
    assert service.repository is not None, "Service should have repository"
    assert service.logger is not None, "Service should have logger"

# Step 4: Test cache system
@pytest.mark.asyncio
async def test_cache_system(mock_services):
    """Test if caching is working."""
    cache = mock_services.cache_manager
    
    # Check initialization
    assert cache.is_initialized, "Cache should be initialized"
    
    # Test basic cache operations
    try:
        # Set a test value
        await cache.set("test-key", "test-value", ttl=60)
        
        # Get the value back
        value = await cache.get("test-key")
        assert value == "test-value", "Cache get/set should work"
        
        # Delete the value
        await cache.delete("test-key")
        value = await cache.get("test-key")
        assert value is None, "Deleted cache key should return None"
    except Exception as e:
        pytest.fail(f"Cache operation failed: {str(e)}")

# Step 5: Test metrics system
@pytest.mark.asyncio
async def test_metrics_system(mock_services):
    """Test if metrics system is working."""
    metrics = mock_services.metrics_manager
    
    # Check initialization
    assert metrics.is_initialized, "Metrics should be initialized"
    
    # Test metric recording
    try:
        # Record a test metric
        metrics.counter("test_counter").inc()
        metrics.gauge("test_gauge").set(42)
        
        # Get metric values
        counter_value = metrics.counter("test_counter")._value.get()
        gauge_value = metrics.gauge("test_gauge")._value.get()
        
        assert counter_value == 1, "Counter should be incremented"
        assert gauge_value == 42, "Gauge should be set"
    except Exception as e:
        pytest.fail(f"Metrics operation failed: {str(e)}")

# Step 6: Test external service connections
@pytest.mark.asyncio
async def test_external_services(mock_services):
    """Test if external service clients are working."""
    # Test Strapi connection
    strapi = mock_services.strapi_client
    assert strapi.is_initialized, "Strapi client should be initialized"
    
    # Test Weaviate connection
    weaviate = mock_services.weaviate_client
    assert weaviate.is_initialized, "Weaviate client should be initialized"
    
    try:
        # Test Strapi health
        await strapi.health_check()
        
        # Test Weaviate health
        await weaviate.health_check()
    except Exception as e:
        pytest.fail(f"External service check failed: {str(e)}") 