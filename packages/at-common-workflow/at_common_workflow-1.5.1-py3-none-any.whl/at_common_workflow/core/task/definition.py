from typing import Callable, Any, Dict, Optional, Type
from pydantic import BaseModel

class TaskDefinition:
    """
    Holds the configuration for a task in the workflow.
    
    This class separates the task definition (what the task is) from
    the task building process (how it's created) and from task execution (how it runs).
    """
    
    def __init__(self, name: str):
        """
        Initialize a task definition with a name.
        
        Args:
            name: The name of the task
        """
        self.name = name
        self.description: Optional[str] = None
        self.input_model: Optional[Type[BaseModel]] = None
        self.output_model: Optional[Type[BaseModel]] = None
        self.progress_model: Optional[Type[BaseModel]] = None
        self.processor_function: Optional[Callable] = None
        
        # Arguments and result configuration
        self.argument_mappings: Dict[str, Any] = {}
        self.result_key: Optional[str] = None
        self.result_path: Optional[str] = None
    
    def __repr__(self) -> str:
        """String representation of the task definition."""
        return f"TaskDefinition(name={self.name}, input={self.input_model.__name__ if self.input_model else None}, output={self.output_model.__name__ if self.output_model else None})"
    
    def is_complete(self) -> bool:
        """
        Check if the task definition has all required components.
        
        Returns:
            bool: True if all required components are specified
        """
        return (
            self.input_model is not None and
            self.output_model is not None and
            self.processor_function is not None and
            self.result_key is not None
        ) 