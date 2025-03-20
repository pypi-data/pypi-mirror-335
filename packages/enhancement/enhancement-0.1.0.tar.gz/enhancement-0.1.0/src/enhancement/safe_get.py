from typing import Any, Dict, TypeVar

T = TypeVar('T')

def get_safe(dictionary: Dict[str, Any], key: str, defvalue: T) -> T:
    """
    Safely retrieve a value from a dictionary.
    Returns the default value if the key doesn't exist or if the value is None.
    
    Args:
        dictionary: The dictionary to search in
        key: The key to look up
        defvalue: The default value to return if the key is not found or value is None
        
    Returns:
        The value if found and not None, otherwise the default value
    """
    value = dictionary.get(key)
    return value if value is not None else defvalue

def get_safe_object(obj: Any, key: str, defvalue: T) -> T:
    """
    Safely retrieve an attribute from an object.
    Returns the default value if the attribute doesn't exist.
    
    Args:
        obj: The object to get the attribute from
        key: The attribute name to look up
        defvalue: The default value to return if the attribute is not found
        
    Returns:
        The attribute value if found, otherwise the default value
    """
    try:
        return getattr(obj, key)
    except AttributeError:
        return defvalue
    