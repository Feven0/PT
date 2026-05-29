"""Test helpers."""
import os
import pytest
from typing import Dict, Any, Optional, Generator
import asyncio
from contextlib import contextmanager

from core.config import AppConfig
from .mock_config import create_mock_config, create_test_container

@pytest.fixture
def mock_config() -> AppConfig:
    """Fixture that provides mock configuration."""
    return create_mock_config()

@pytest.fixture
def test_container(mock_config: AppConfig):
    """Fixture that provides test container with mock configuration."""
    return create_test_container(mock_config)

@contextmanager
def mock_env_vars(env_vars: Dict[str, str]) -> Generator[None, None, None]:
    """Context manager for temporarily setting environment variables.
    
    Args:
        env_vars: Dictionary of environment variables to set
        
    Yields:
        None
    """
    original_vars = {}
    
    try:
        # Save original values
        for key in env_vars:
            if key in os.environ:
                original_vars[key] = os.environ[key]
                
        # Set test values
        os.environ.update(env_vars)
        yield
        
    finally:
        # Restore original values
        for key in env_vars:
            if key in original_vars:
                os.environ[key] = original_vars[key]
            else:
                del os.environ[key]

@pytest.fixture
async def mock_services(test_container):
    """Fixture that initializes and cleans up test services.
    
    Args:
        test_container: Test container instance
        
    Yields:
        Test container instance
    """
    try:
        await test_container.initialize()
        await test_container.start()
        yield test_container
    finally:
        await test_container.stop()
        await test_container.cleanup()

def get_test_config(overrides: Optional[Dict[str, Any]] = None) -> AppConfig:
    """Get test configuration with optional overrides.
    
    Args:
        overrides: Optional configuration overrides
        
    Returns:
        Test configuration instance
    """
    config = create_mock_config()
    
    if overrides:
        for key, value in overrides.items():
            setattr(config, key, value)
            
    return config 