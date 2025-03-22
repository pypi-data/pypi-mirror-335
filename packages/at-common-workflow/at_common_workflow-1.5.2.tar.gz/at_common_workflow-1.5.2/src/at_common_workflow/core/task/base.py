from typing import Generic, TypeVar, Optional, Protocol, runtime_checkable
from pydantic import BaseModel

InputType = TypeVar('InputType', bound=BaseModel)
OutputType = TypeVar('OutputType', bound=BaseModel) 

@runtime_checkable
class TaskProtocol(Protocol[InputType, OutputType]):
    """Protocol for task interfaces that can be used in workflows."""
    name: str
    
    def _validate(self) -> None:
        """Validate task configuration."""
        ...

class BaseTask(Generic[InputType, OutputType]):
    """
    Base class for all task types in a workflow.
    
    A task:
    - Has a unique identifier (name)
    - Has an optional description
    - Defines validation logic for its configuration
    - Serves as a foundation for concrete task implementations
    """
    
    def __init__(
        self, 
        name: str, 
        description: Optional[str] = None
    ):
        """
        Initialize a task with its basic configuration.
        
        Args:
            name: Unique task identifier
            description: Optional human-readable description
            
        Raises:
            ValueError: If name is empty or None
        """
        if not name:
            raise ValueError("Task name cannot be empty")
            
        self.name = name
        self.description = description
        
    def _validate(self) -> None:
        """
        Validate that task configuration is properly defined.
        To be implemented by subclasses.
        
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement _validate method")
    
    def __repr__(self) -> str:
        """String representation of the task."""
        return f"{self.__class__.__name__}(name={self.name!r}, description={self.description!r})"
        
    def __str__(self) -> str:
        """Human-readable representation of the task."""
        if self.description:
            return f"{self.name}: {self.description}"
        return self.name