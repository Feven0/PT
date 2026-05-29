"""Basic app health tests."""
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from .helpers import get_test_config

# Step 1: Basic fixtures
@pytest.fixture
def test_app(mock_config) -> FastAPI:
    """Create a test FastAPI application."""
    from app import create_app  # Import your app creation function
    app = create_app()
    app.state.config = mock_config
    return app

@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    """Create a test client."""
    return TestClient(test_app)

# Step 2: Basic health check test
def test_app_health(client: TestClient):
    """Test if the app is responding to health checks."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

# Step 3: Test app configuration
def test_app_configuration(test_app: FastAPI):
    """Test if app has basic configuration."""
    assert hasattr(test_app.state, "config"), "App should have a config"
    assert test_app.state.config is not None, "Config should be initialized"

# Step 4: Test core services
def test_core_services(mock_services):
    """Test if core services are available."""
    # Check core managers
    assert mock_services.metrics_manager is not None, "Metrics manager should be available"
    assert mock_services.cache_manager is not None, "Cache manager should be available"
    assert mock_services.logger is not None, "Logger should be available"

# Step 5: Test database connection
@pytest.mark.asyncio
async def test_database_connection(mock_services):
    """Test if database connection is working."""
    try:
        # Try a simple database operation
        await mock_services.database.ping()
        connection_ok = True
    except Exception as e:
        connection_ok = False
        pytest.fail(f"Database connection failed: {str(e)}")
    
    assert connection_ok, "Database connection should be successful" 