"""Test container initialization with mock configuration."""
import pytest
from core.di.container import Container, ContainerError
from .helpers import mock_config, test_container, mock_env_vars, mock_services

def test_container_initialization(mock_config):
    """Test container initialization with mock config."""
    container = Container(mock_config)
    assert container.config == mock_config
    assert container.metrics_manager is not None
    assert container.cache_manager is not None
    assert container.alert_manager is not None

def test_container_with_invalid_config():
    """Test container initialization with invalid config."""
    invalid_config = mock_config()
    invalid_config.strapi.base_url = None  # Make config invalid
    
    with pytest.raises(ContainerError) as exc_info:
        Container(invalid_config)
    assert "Invalid type for config field base_url" in str(exc_info.value)

@pytest.mark.asyncio
async def test_container_lifecycle(mock_services):
    """Test container lifecycle with mock services."""
    container = mock_services
    
    # Check core managers
    assert container.metrics_manager.is_initialized
    assert container.cache_manager.is_initialized
    assert container.alert_manager.is_initialized
    
    # Check infrastructure clients
    assert container.strapi_client.is_initialized
    assert container.weaviate_client.is_initialized
    
    # Check repositories
    assert container.user_repository.is_initialized
    assert container.interview_repository.is_initialized
    assert container.session_repository.is_initialized
    
    # Check services
    assert container.websocket_service.is_initialized
    assert container.webrtc_service.is_initialized
    assert container.chat_service.is_initialized

def test_container_with_env_vars():
    """Test container initialization with environment variables."""
    test_env = {
        "STRAPI_API_URL": "http://test-strapi:1337",
        "STRAPI_AUTH_TOKEN": "test-token",
        "WEAVIATE_API_URL": "http://test-weaviate:8080",
        "WEAVIATE_API_KEY": "test-key"
    }
    
    with mock_env_vars(test_env):
        container = Container(mock_config())
        assert container.config.strapi.base_url == "http://test-strapi:1337"
        assert container.config.strapi.api_token == "test-token"
        assert container.config.weaviate.url == "http://test-weaviate:8080"
        assert container.config.weaviate.api_key == "test-key" 