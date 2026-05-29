"""Core base package."""
from .lifecycle import LifecycleAware
from .component import BaseComponent
from .service import BaseService
from .repository import BaseRepository
from .decorators import component, injectable, service, repository, depends_on

__all__ = [
    'LifecycleAware',
    'BaseComponent',
    'BaseService',
    'BaseRepository',
    'component',
    'injectable',
    'service',
    'repository',
    'depends_on',
] 