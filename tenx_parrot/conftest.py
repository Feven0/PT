"""Root conftest.py for backend tests."""
import os
import sys
from pathlib import Path
import pytest

# Create a namespace for sharing data between conftest files
pytest.test_env = {}

def pytest_configure(config):
    """Configure pytest."""
    print("\nRoot conftest.py: Configuring pytest")
    
    # Get absolute path to backend directory
    backend_dir = Path(__file__).parent.absolute()
    
    # Ensure backend directory is in Python path
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    
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
    
    print("Root conftest.py: Configuration complete")

def pytest_sessionstart(session):
    """Set up test session."""
    print("\nRoot conftest.py: Setting up test session")
    print("Python path:")
    for path in sys.path:
        print(f"  {path}")

def pytest_sessionfinish(session, exitstatus):
    """Clean up test session."""
    print("\nRoot conftest.py: Cleaning up test session")