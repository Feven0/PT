"""Test to verify path resolution."""
import os
import sys
from pathlib import Path
import pytest

def test_python_path(backend_dir, test_dir):
    """Verify that Python path is set correctly."""
    # Print current paths for debugging
    # print("\nCurrent paths:")
    # print(f"Backend dir: {backend_dir}")
    # print(f"Test dir: {test_dir}")
    # print(f"Python path: {sys.path}")
    
    # Verify backend directory is in path
    assert str(backend_dir) in sys.path, f"Backend directory {backend_dir} not in Python path"
    
    # Verify PYTHONPATH
    pythonpath = os.environ.get("PYTHONPATH", "")
    assert str(backend_dir) in pythonpath, f"Backend directory {backend_dir} not in PYTHONPATH"
    
    # Verify we can import from backend
    try:
        os.environ.setdefault("USE_MOCK_CONFIG", "true")
        import app
        print("Successfully imported app module")
        os.environ.setdefault("USE_MOCK_CONFIG", "false")
    except ImportError as e:
        pytest.fail(f"Failed to import app module: {e}") 