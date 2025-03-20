import functools
import inspect
from typing import Any, Callable, TypeVar

T = TypeVar('T')

def cache_result(wrapped_func: Callable[..., T]) -> Callable[..., T]:
    """
    A decorator that caches the results of a function call.
    
    Args:
        wrapped_func: The function to be wrapped with caching functionality.
        
    Returns:
        A wrapped function that implements caching of results.
        
    The wrapped function includes a reset_cache() method to clear the cache.
    """
    # Get the parameter names of the wrapped function
    params = inspect.signature(wrapped_func).parameters
    
    @functools.wraps(wrapped_func)
    def wrapper_func(*args: Any, **kwargs: Any) -> T:
        try:
            # Convert positional arguments to keyword arguments
            bound_args = inspect.signature(wrapped_func).bind(*args, **kwargs)
            bound_args.apply_defaults()
            # Create a normalized key from all arguments as kwargs
            key = tuple(sorted(bound_args.arguments.items()))
            
            res = wrapper_func._results_cache.get(key)
            if res is None:
                res = wrapper_func._results_cache[key] = wrapped_func(*args, **kwargs)
            return res
        except TypeError:
            # Fall back to calling the function directly if arguments are unhashable
            return wrapped_func(*args, **kwargs)

    # Type declaration for cache
    wrapper_func._results_cache = {} 

    def reset_cache() -> None:
        """Clears the cache of stored results."""
        wrapper_func._results_cache.clear()

    wrapper_func.reset_cache = reset_cache
    return wrapper_func