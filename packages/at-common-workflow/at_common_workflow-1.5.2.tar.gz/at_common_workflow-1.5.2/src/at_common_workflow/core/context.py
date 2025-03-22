from typing import Any, Dict, Optional, Union, TypeVar, List, cast, Mapping, Iterator
from threading import RLock
import copy
import json

T = TypeVar('T')

class Context:
    """
    A thread-safe dictionary-like store for workflow execution data.
    
    Features:
    - Thread-safe access with recursive locking
    - Dot notation access (context.user.name)
    - String path access with dot notation (context.get("user.name"))
    - Deep copying for isolation
    - JSON serialization support
    
    Args:
        initial_data: Optional dictionary to initialize the context with
    """
    def __init__(self, initial_data: Optional[Dict[str, Any]] = None) -> None:
        self._data: Dict[str, Any] = {}
        self._lock = RLock()  # Using RLock to allow recursive locking
        
        if initial_data:
            self.update(initial_data)
    
    def __getattr__(self, key: str) -> Any:
        """Access context values using attribute notation."""
        with self._lock:
            return self.get(key)
    
    def __setattr__(self, key: str, value: Any) -> None:
        """Set context values using attribute notation."""
        if key in ('_data', '_lock'):
            super().__setattr__(key, value)
        else:
            with self._lock:
                self.set(key, value)
    
    def _validate_key(self, key: str) -> None:
        """
        Validate that a key is not None or empty.
        
        Args:
            key: Key to validate
            
        Raises:
            AttributeError: If key is None
            KeyError: If key is empty
        """
        if key is None:
            raise AttributeError("Key cannot be None")
        if not key:
            raise KeyError("Key cannot be empty")
    
    def get(self, key: str, default: Optional[T] = None) -> Union[Any, T]:
        """
        Get value using dot notation for nested access.
        
        Args:
            key: Key to look up, can use dot notation for nested access
            default: Value to return if key is not found
        
        Returns:
            The value if found, otherwise the default value
            
        Raises:
            KeyError: If the key is not found and no default value is provided
            AttributeError: If key is None
        """
        with self._lock:
            self._validate_key(key)
                
            parts = key.split('.')
            current = self._data
            
            for i, part in enumerate(parts):
                if not isinstance(current, Mapping):
                    if default is None:
                        path = '.'.join(parts[:i])
                        raise KeyError(f"Cannot access '{part}' in '{key}': '{path}' is not a dictionary")
                    return default
                    
                if part not in current:
                    if default is None:
                        raise KeyError(f"Key '{key}' not found in context")
                    return default
                    
                current = current[part]
                
            return current
    
    def contains_key(self, key: str) -> bool:
        """
        Check if a key exists in the context.
        Supports dot notation for nested keys.
        
        Args:
            key: Key to check, can use dot notation for nested access
            
        Returns:
            bool: True if the key exists, False otherwise
        """
        try:
            self.get(key)
            return True
        except (KeyError, AttributeError):
            return False
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value using dot notation for nested access.
        
        Creates intermediate dictionaries as needed for nested keys.
        
        Args:
            key: Key to set, can use dot notation for nested access
            value: Value to store
            
        Raises:
            AttributeError: If key is None
            KeyError: If key is empty
        """
        with self._lock:
            self._validate_key(key)
                
            parts = key.split('.')
            current = self._data
            
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    # Convert non-dict to dict if needed for nested keys
                    current[part] = {}
                current = current[part]
                
            current[parts[-1]] = value
            
    def copy(self) -> 'Context':
        """
        Create a deep copy of this context.
        
        Returns:
            Context: A new Context instance with the same data
        """
        with self._lock:
            new_context = Context()
            new_context._data = copy.deepcopy(self._data)
            return new_context
    
    def update(self, other: Union[Dict[str, Any], 'Context']) -> None:
        """
        Update this context with values from another context or dictionary.
        
        Args:
            other: Another Context instance or dictionary to update from
        """
        with self._lock:
            if isinstance(other, Context):
                with other._lock:
                    self._data.update(copy.deepcopy(other._data))
            else:
                self._data.update(copy.deepcopy(other))

    def __contains__(self, key: str) -> bool:
        """Support 'in' operator for checking key existence."""
        try:
            self.get(key)
            return True
        except (KeyError, AttributeError):
            return False
    
    def keys(self) -> List[str]:
        """Get top-level keys in the context."""
        with self._lock:
            return list(self._data.keys())
    
    def items(self) -> List[tuple]:
        """Get top-level items (key-value pairs) in the context."""
        with self._lock:
            return list(self._data.items())
    
    def __iter__(self) -> Iterator[str]:
        """Support iteration over top-level keys."""
        with self._lock:
            return iter(self._data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the context to a dictionary.
        
        Returns:
            Dict: Deep copy of the internal data structure
        """
        with self._lock:
            return copy.deepcopy(self._data)
    
    def to_json(self) -> str:
        """
        Convert the context to a JSON string.
        
        Returns:
            str: JSON representation of the context
            
        Raises:
            TypeError: If the context contains values that cannot be serialized to JSON
        """
        with self._lock:
            return json.dumps(self._data)
    
    def __repr__(self) -> str:
        """Provide readable string representation."""
        return f"Context({self._data})"