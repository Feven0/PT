"""Base decorators."""
from typing import Optional, Dict, Any, Callable, TypeVar, Union, List, Type
from functools import wraps
from ..types.metrics import MetricsProtocol


T = TypeVar('T')  # Generic type for all components


def component(
    name: str,
    metrics: Optional[List[Dict[str, Any]]] = None,
    dependencies: Optional[List[str]] = None
) -> Callable[[Type[T]], Type[T]]:
    """Component decorator.
    
    Args:
        name: Component name
        metrics: Optional list of metric definitions
        dependencies: Optional list of component dependencies
        
    Returns:
        Decorated component class
    """
    def decorator(cls: Type[T]) -> Type[T]:
        original_init = cls.__init__
        
        @wraps(original_init)
        def init_wrapper(self: Any, *args: Any, **kwargs: Any) -> None:
            # Call original init
            original_init(self, *args, **kwargs)
            
            # Set component name
            self.name = name
            
            # Register metrics if provided
            if metrics and hasattr(self, 'metrics') and isinstance(self.metrics, MetricsProtocol):
                for metric in metrics:
                    self.metrics.register_metric(**metric)
                    
            # Register dependencies if provided
            if dependencies and hasattr(self, 'add_dependency'):
                for dep in dependencies:
                    self.add_dependency(dep)
                    
        cls.__init__ = init_wrapper
        return cls
        
    return decorator


def injectable(
    name: str,
    scope: str = "singleton"
) -> Callable[[Type[T]], Type[T]]:
    """Injectable decorator for dependency injection.
    
    Args:
        name: Component name
        scope: Injection scope (singleton, request, transient)
        
    Returns:
        Decorated class
    """
    def decorator(cls: Type[T]) -> Type[T]:
        setattr(cls, "__di_name__", name)
        setattr(cls, "__di_scope__", scope)
        return cls
        
    return decorator


def service(
    name: str,
    metrics: Optional[List[Dict[str, Any]]] = None,
    dependencies: Optional[List[str]] = None
) -> Callable[[Type[T]], Type[T]]:
    """Service decorator.
    
    Args:
        name: Service name
        metrics: Optional list of metric definitions
        
    Returns:
        Decorated service class
    """
    def decorator(cls: Type[T]) -> Type[T]:
        # Apply component decorator first
        cls = component(name=name, 
                        metrics=metrics, 
                        dependencies=dependencies)(cls)
        
        # Mark as service
        setattr(cls, "__service__", True)
        return cls
        
    return decorator


def repository(
    name: str,
    metrics: Optional[List[Dict[str, Any]]] = None,
    dependencies: Optional[List[str]] = None
) -> Callable[[Type[T]], Type[T]]:
    """Repository decorator.
    
    Args:
        name: Repository name
        metrics: Optional list of metric definitions
        
    Returns:
        Decorated repository class
    """
    def decorator(cls: Type[T]) -> Type[T]:
        # Apply component decorator first
        cls = component(name=name, 
                        metrics=metrics,
                        dependencies=dependencies)(cls)
        
        # Mark as repository
        setattr(cls, "__repository__", True)
        return cls
        
    return decorator


def depends_on(*component_names: str) -> Callable[[Type[T]], Type[T]]:
    """Decorator to specify component dependencies.
    
    Args:
        *component_names: Names of components this component depends on
        
    Returns:
        Decorated class
    """
    def decorator(cls: Type[T]) -> Type[T]:
        original_init = cls.__init__
        
        @wraps(original_init)
        def init_wrapper(self: Any, *args: Any, **kwargs: Any) -> None:
            original_init(self, *args, **kwargs)
            if hasattr(self, 'add_dependency'):
                for name in component_names:
                    self.add_dependency(name)
                    
        cls.__init__ = init_wrapper
        return cls
        
    return decorator 