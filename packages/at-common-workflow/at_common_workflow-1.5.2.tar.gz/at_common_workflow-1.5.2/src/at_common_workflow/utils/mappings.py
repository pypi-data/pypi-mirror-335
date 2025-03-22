from typing import Any, Optional, Union, Dict, List, Set, TypeVar, Generic
from pydantic import BaseModel

from at_common_workflow.core.context import Context
from at_common_workflow.core.exceptions import ContextError, format_error

T = TypeVar('T')

def get_nested_value(obj: Any, path: str) -> Any:
    """
    Get a value from a nested object using a dot-separated path.
    
    Args:
        obj: The object to get the value from
        path: Dot-separated path to the value
        
    Returns:
        Any: The value at the path
        
    Raises:
        AttributeError: If the path doesn't exist in the object
    """
    if not path or path == '':
        return obj
        
    parts = path.split('.')
    current = obj
    
    for part in parts:
        if hasattr(current, part):
            current = getattr(current, part)
        elif isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise AttributeError(f"Cannot access '{part}' in path '{path}'")
            
    return current

class BaseMapping:
    """Base class for all mapping types."""
    
    def __eq__(self, other: object) -> bool:
        """
        Compare two mapping instances for equality.
        
        Args:
            other: Another mapping instance to compare with
            
        Returns:
            bool: True if the mappings are equal, False otherwise
        """
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self) -> int:
        """
        Generate a hash value for this mapping.
        
        Returns:
            int: Hash value
        """
        return hash(tuple(sorted(self.__dict__.items())))
    
    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"

class ArgumentMapping(BaseMapping):
    """Maps context values or constants to task arguments."""
    
    def __init__(self, value: Union[str, Any], mapping_dict: Optional[Dict[str, Union[str, Any]]] = None):
        self.value = value
        self.mapping_dict = mapping_dict
        self.is_context_ref = isinstance(value, str) and value.startswith("$")
        self.has_mapping_dict = mapping_dict is not None
        self._context_refs: Optional[List[str]] = None
    
    @classmethod
    def from_constant(cls, value: Any) -> 'ArgumentMapping':
        """Create an ArgumentMapping from a constant value."""
        return cls(value=value)
        
    @classmethod
    def from_context(cls, context_key: str) -> 'ArgumentMapping':
        """Create an ArgumentMapping from a context reference."""
        if not context_key.startswith('$'):
            context_key = f"${context_key}"
        return cls(value=context_key)
        
    @classmethod
    def from_context_with_path(cls, context_mapping: Dict[str, str]) -> 'ArgumentMapping':
        """Create an ArgumentMapping from a context mapping with nested paths."""
        # Ensure context keys have $ prefix
        mapping_dict = {k: f"${v}" if not v.startswith('$') else v 
                       for k, v in context_mapping.items()}
        return cls(
            value=f"${next(iter(context_mapping.keys()))}", 
            mapping_dict=mapping_dict
        )
    
    def get_context_refs(self) -> List[str]:
        """
        Get all context references used in this mapping.
        
        Returns:
            List[str]: List of context reference keys (without $ prefix)
        """
        if self._context_refs is not None:
            return self._context_refs
            
        refs: List[str] = []
        if self.is_context_ref:
            refs.append(self.value[1:])  # Remove $ prefix
        if self.has_mapping_dict and self.mapping_dict:
            refs.extend(value[1:] for key, value in self.mapping_dict.items() 
                      if isinstance(value, str) and value.startswith('$'))
        
        self._context_refs = refs
        return refs
        
    def validate_context_refs(self, context: Context) -> List[str]:
        """
        Check if all context references exist in the provided context.
        
        Args:
            context: The context to validate against
            
        Returns:
            List[str]: List of references that don't exist in the context
            
        Raises:
            ContextError: If context is None
        """
        if context is None:
            raise ContextError("Context cannot be None")
            
        # Return list of references that are not in the context
        return [ref for ref in self.get_context_refs() if not context.contains_key(ref)]

    def resolve(self, context: Context) -> Any:
        """
        Resolve the mapping value from context if it's a reference.
        
        Args:
            context: Context object to resolve references from
            
        Returns:
            Any: Resolved value or dictionary of resolved values
            
        Raises:
            KeyError: If a referenced context key doesn't exist
            ContextError: If context is None
            AttributeError: If a nested path doesn't exist
        """
        if context is None:
            raise ContextError("Context cannot be None")
            
        if self.has_mapping_dict and self.mapping_dict:
            result = {}
            for key, context_key in self.mapping_dict.items():
                if isinstance(context_key, str) and context_key.startswith('$'):
                    try:
                        # Handle nested paths like "result.value"
                        ctx_key = context_key[1:]  # Remove $ prefix
                        if '.' in ctx_key:
                            base_key, path = ctx_key.split('.', 1)
                            base_obj = context.get(base_key)
                            result[key] = get_nested_value(base_obj, path)
                        else:
                            result[key] = context.get(ctx_key)
                    except KeyError:
                        raise KeyError(f"Context key '{context_key[1:]}' not found for mapping key '{key}'")
                    except AttributeError as e:
                        raise AttributeError(f"Error accessing nested path in '{context_key[1:]}': {str(e)}")
                else:
                    result[key] = context_key
            return result
            
        if self.is_context_ref:
            try:
                # Handle nested paths like "result.value"
                ctx_key = self.value[1:]  # Remove $ prefix
                if '.' in ctx_key:
                    base_key, path = ctx_key.split('.', 1)
                    base_obj = context.get(base_key)
                    return get_nested_value(base_obj, path)
                else:
                    return context.get(ctx_key)
            except KeyError:
                raise KeyError(f"Context key '{self.value[1:]}' not found")
            except AttributeError as e:
                raise AttributeError(f"Error accessing nested path in '{self.value[1:]}': {str(e)}")
            
        return self.value

class ResultMapping(BaseMapping, Generic[T]):
    """Maps task results to context keys."""
    
    def __init__(self, context_key: str, result_path: Optional[str] = None):
        """
        Initialize a ResultMapping.
        
        Args:
            context_key: Context key to store the result (can use dot notation for nested storage)
            result_path: Optional attribute path to extract from the result
        """
        self.context_key = context_key
        self.result_path = result_path
    
    def store(self, context: Context, result: T) -> None:
        """
        Store the task result in the context.
        
        Args:
            context: Context object to store the result in
            result: Task result to store
            
        Raises:
            AttributeError: If result_path is specified but doesn't exist in the result
            ContextError: If context is None
        """
        if context is None:
            raise ContextError("Context cannot be None")
            
        if self.result_path:
            # Extract the value from the result using the result_path
            try:
                value = get_nested_value(result, self.result_path)
            except AttributeError:
                raise AttributeError(f"Result does not have nested attribute '{self.result_path}'")
        else:
            value = result
            
        # Store the value in the context using the context_key
        # Context.set() already supports nested keys with dot notation
        context.set(self.context_key, value)