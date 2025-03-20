from typing import Any, List, Iterator, TypeVar
from enhancement.ndict import ndict

T = TypeVar('T')

class Iterable:
    """A wrapper class around ndict providing dictionary-like functionality with nested dictionary support.
    
    This class implements the standard dictionary interface while providing automatic nested dictionary
    creation through the underlying ndict implementation.
    """
    
    def __init__(self) -> None:
        """Initialize an empty Iterable instance."""
        self.data = ndict()

    def __iter__(self) -> Iterator[Any]:
        """Return an iterator over the dictionary's keys."""
        return self.data.__iter__()
    
    def __len__(self) -> int:
        """Return the number of items in the dictionary."""
        return len(self.data)
    
    def __contains__(self, v: Any) -> bool:
        """Return True if the dictionary has the specified key, else False."""
        return v in self.data
    
    def __getitem__(self, v: Any) -> Any:
        """Return the value for key v."""
        return self.data[v]
    
    def __setitem__(self, k: Any, v: Any) -> None:
        """Set the value for key k to v."""
        self.data[k] = v

    def keys(self) -> Iterator[Any]:
        """Return an iterator over the dictionary's keys."""
        return self.data.keys()
    
    def items(self) -> Iterator[tuple[Any, Any]]:
        """Return an iterator over the dictionary's (key, value) pairs."""
        return self.data.items()
    
    def values(self) -> Iterator[Any]:
        """Return an iterator over the dictionary's values."""
        return self.data.values()
    
    def clear(self) -> None:
        """Remove all items from the dictionary."""
        self.data.clear()

class IterableList:
    """A wrapper class around list providing list-like functionality.
    
    This class implements the standard list interface while providing additional
    safety checks and convenience methods.
    """
    
    def __init__(self) -> None:
        """Initialize an empty IterableList instance."""
        self.data: List[Any] = []

    def __iter__(self) -> Iterator[Any]:
        """Return an iterator over the list's values."""
        return self.data.__iter__()
    
    def __len__(self) -> int:
        """Return the number of items in the list."""
        return len(self.data)
    
    def __contains__(self, v: Any) -> bool:
        """Return True if v is in the list, else False."""
        return v in self.data

    def __getitem__(self, v: int) -> Any:
        """Return the item at index v."""
        return self.data[v]
    
    def __setitem__(self, k: int, v: Any) -> None:
        """Set the item at index k to v."""
        # Extend the list if necessary
        while len(self.data) <= k:
            self.data.append(None)
        self.data[k] = v

    def index(self, v: Any) -> int:
        """Return the index of the first occurrence of v.
        
        Raises:
            ValueError: If the value is not present in the list.
        """
        return self.data.index(v)
    
    def append(self, v: Any) -> None:
        """Append an item to the end of the list."""
        self.data.append(v)
    
    def insert(self, index: int, v: Any) -> None:
        """Insert an item at a given position."""
        self.data.insert(index, v)
    
    def pop(self, index: int = -1) -> Any:
        """Remove and return item at index (default last)."""
        return self.data.pop(index)
    
    def remove(self, v: Any) -> None:
        """Remove first occurrence of value v.
        
        Raises:
            ValueError: If the value is not present in the list.
        """
        self.data.remove(v)
    
    def clear(self) -> None:
        """Remove all items from the list."""
        self.data.clear()
    
    def extend(self, iterable: Iterator[Any]) -> None:
        """Extend list by appending elements from the iterable."""
        self.data.extend(iterable)
    
    def __str__(self) -> str:
        """Return a string representation of the list."""
        return str(self.data)
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the list."""
        return f"IterableList({self.data})"