"""Dependency injection module."""
from contextlib import contextmanager
import threading
from typing import Optional

from .container import Container


_container: Optional[Container] = None
_container_lock = threading.Lock()


def get_container() -> Optional[Container]:
    """Get current container instance.
    
    Returns:
        Current container instance if set
    """
    return _container


@contextmanager
def container_context(container: Container):
    """Context manager for container scope.
    
    Args:
        container: Container instance
    """
    global _container
    
    with _container_lock:
        previous = _container
        _container = container
        try:
            yield container
        finally:
            _container = previous


__all__ = [
    "Container",
    "get_container",
    "container_context"
] 