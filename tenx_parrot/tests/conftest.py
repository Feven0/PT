"""Test configuration and fixtures."""
import os
import sys
import pytest
from pathlib import Path
from typing import Dict, Any



# Re-export fixtures from helpers
from tests.helpers import (
    mock_config,
    test_container,
    mock_services,
    mock_env_vars,
    get_test_config
)

# Get the backend directory path
BACKEND_DIR = Path(__file__).parent.parent.absolute()

# Ensure backend directory is in Python path
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Create a namespace for sharing data between conftest files
pytest.test_env = {}

def pytest_configure(config):
    """Configure pytest."""
    print("\nTests conftest.py: Configuring pytest")
    
    
    # Ensure backend directory is in Python path
    if str(BACKEND_DIR) not in sys.path:
        sys.path.insert(0, str(BACKEND_DIR))
    
    # Store base environment variables in pytest namespace
    pytest.test_env["base_env_vars"] = {
        "ENVIRONMENT": "test",
        "MOCK_EXTERNAL_SERVICES": "true",
        "TEST_TIMEOUT": "30",
        "ASYNC_TEST_TIMEOUT": "60"
    }
    
    # Set environment variables
    for key, value in pytest.test_env["base_env_vars"].items():
        os.environ.setdefault(key, value)
    
    # Set PYTHONPATH
    os.environ.setdefault("PYTHONPATH", str(backend_dir))
    
    print("Tests conftest.py: Configuration complete")

def pytest_sessionstart(session):
    """Start a pytest session"""
    print("\nTests conftest.py: Starting pytest session ...\n")

def pytest_sessionfinish(session, exitstatus):
    """Clean up test session."""
    print("\nTests conftest.py: Cleaning up test session")



@pytest.fixture(scope="session")
def backend_dir():
    """Provide the backend directory path."""
    return BACKEND_DIR

@pytest.fixture(scope="session")
def test_dir():
    """Provide the test directory path."""
    return BACKEND_DIR / "tests"

@pytest.fixture(scope="session")
def env_vars():
    """Provide test environment variables."""
    print("Tests conftest.py: Setting up env_vars fixture")
    
    # Start with base environment variables from root conftest    
    base_vars = pytest.test_env["base_env_vars"].copy()
    
    # Add test-specific variables
    vars = base_vars.copy()
    vars.update({
        "PYTHONPATH": str(BACKEND_DIR),
        "STRAPI_API_URL": "http://test-strapi:1337",
        "STRAPI_AUTH_TOKEN": "test-token",
        "WEAVIATE_API_URL": "http://test-weaviate:8080",
        "WEAVIATE_API_KEY": "test-key"
    })
    return vars

@pytest.fixture(autouse=True)
def setup_test_env(env_vars):
    """Set up test environment variables."""
    print("\nTests conftest.py: Setting up test environment")
    
    # Store original env vars
    original_env = {}
    for key, value in env_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield
    
    # Restore original env vars
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value