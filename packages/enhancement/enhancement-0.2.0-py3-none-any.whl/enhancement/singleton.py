from threading import Lock
from typing import Dict, Any, TypeVar, Type

T = TypeVar('T')

class Singleton(type):
    """
    Singleton type is a metaclass enforcing the children classes instances are unique during runtime.
    This implementation is thread-safe and provides methods to manage instances.
    
    Use cases:
    ```python
    class MyClass(BaseClass, metaclass=Singleton):
        pass
    ```
    """
    _instances: Dict[Type, Any] = {}
    _lock: Lock = Lock()

    def __call__(cls: Type[T], *args: Any, **kwargs: Any) -> T:
        if cls not in cls._instances:
            with cls._lock:
                # Double-checked locking pattern
                if cls not in cls._instances:
                    cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
    @classmethod
    def reset(cls, target_cls = None) -> None:
        """
        Reset the singleton instance(s).
        
        Args:
            target_cls: Optional; specific class to reset.
                       If None, all instances will be reset.
        """
        with cls._lock:
            if target_cls is not None:
                if target_cls in cls._instances:
                    del cls._instances[target_cls]
            else:
                cls._instances.clear()