from typing import Callable, Any, Dict, Optional, Type, Union, TYPE_CHECKING
from pydantic import BaseModel

from at_common_workflow.utils.mappings import ArgumentMapping, ResultMapping
from at_common_workflow.core.exceptions import TaskConfigurationError, format_error
from .processing_task import ProcessingTask
from .definition import TaskDefinition
from .validation import TaskValidator

if TYPE_CHECKING:
    from at_common_workflow.core.workflow import WorkflowBuilder

class TaskBuilder:
    """
    Builder for creating and configuring tasks with a fluent interface.
    
    This class provides a fluent API for defining tasks in a workflow.
    It manages the configuration of a task and validates the configuration
    before adding the task to the workflow.
    
    Example:
        workflow_builder.task("add_numbers")
            .input_model(AddInputModel)
            .output_model(AddOutputModel)
            .execute(add_function)
            .arg("a", 5)                  # Constant argument
            .arg("b", from_ctx="x")       # Context argument
            .arg("c", from_ctx={"key": "nested.path"})  # Nested path
            .output("result")
    """
    
    def __init__(self, wb: 'WorkflowBuilder', name: str) -> None:
        """Initialize a TaskBuilder with a workflow builder and task name."""
        self._wb = wb
        self._task_def = TaskDefinition(name)
    
    def description(self, description: str) -> 'TaskBuilder':
        """Add a description to the task."""
        self._task_def.description = description
        return self
    
    def input_model(self, model: Type[BaseModel]) -> 'TaskBuilder':
        """
        Set the input model for the task.
        
        Args:
            model: A Pydantic model class for input validation
            
        Returns:
            TaskBuilder: The builder instance for method chaining
            
        Raises:
            TypeError: If model is not a Pydantic BaseModel class
        """
        if not (isinstance(model, type) and issubclass(model, BaseModel)):
            raise TypeError(f"input_model must be a Pydantic BaseModel class, got {type(model).__name__}")
        self._task_def.input_model = model
        return self
    
    def output_model(self, model: Type[BaseModel]) -> 'TaskBuilder':
        """
        Set the output model for the task.
        
        Args:
            model: A Pydantic model class for output validation
            
        Returns:
            TaskBuilder: The builder instance for method chaining
            
        Raises:
            TypeError: If model is not a Pydantic BaseModel class
        """
        if not (isinstance(model, type) and issubclass(model, BaseModel)):
            raise TypeError(f"output_model must be a Pydantic BaseModel class, got {type(model).__name__}")
        self._task_def.output_model = model
        return self
    
    def progress_model(self, model: Type[BaseModel]) -> 'TaskBuilder':
        """
        Set the progress model for the task.
        
        Args:
            model: A Pydantic model class for progress event validation
            
        Returns:
            TaskBuilder: The builder instance for method chaining
            
        Raises:
            TypeError: If model is not a Pydantic BaseModel class
        """
        if not (isinstance(model, type) and issubclass(model, BaseModel)):
            raise TypeError(f"progress_model must be a Pydantic BaseModel class, got {type(model).__name__}")
        self._task_def.progress_model = model
        return self
        
    def processor(self, processor_function: Callable) -> 'TaskBuilder':
        """
        Set the function that will process the task input and produce output.
        
        Args:
            processor_function: The function to execute when the task runs
            
        Returns:
            TaskBuilder: The builder instance for method chaining
        """
        self._task_def.processor_function = processor_function
        return self

    def arg(self, name: str, value: Any = None, from_ctx: Optional[Union[str, Dict[str, str]]] = None) -> 'TaskBuilder':
        """
        Add an argument to the task. Can be a constant value or a context reference.
        
        Args:
            name: Name of the argument
            value: Constant value to use (default if from_ctx not provided)
            from_ctx: Context key or mapping for retrieving value from context
            
        Returns:
            TaskBuilder: The builder instance for method chaining
            
        Examples:
            task.arg("a", 5)  # Constant argument
            task.arg("b", from_ctx="x")  # Single context reference
            task.arg("c", from_ctx={"key": "nested.path"})  # Nested path
        """
        # Determine which type of argument mapping to create
        if from_ctx is not None:
            # Context reference
            if isinstance(from_ctx, str):
                self._task_def.argument_mappings[name] = ArgumentMapping.from_context(from_ctx)
            else:
                self._task_def.argument_mappings[name] = ArgumentMapping.from_context_with_path(from_ctx)
        else:
            # Constant value - but check if it looks like it should be a context ref
            if isinstance(value, str) and value.startswith("$") and "." in value:
                raise TaskConfigurationError(format_error(
                    f"Constant argument '{name}' looks like a context reference: {value}",
                    task_name=self._task_def.name
                ))
                
            self._task_def.argument_mappings[name] = ArgumentMapping.from_constant(value)
            
        return self
    
    def output(self, context_key: str, result_path: Optional[str] = None) -> 'WorkflowBuilder':
        """
        Configure where to store the task result and add task to workflow.
        This finalizes the task configuration and returns the WorkflowBuilder.
        
        Args:
            context_key: Context key to store the result, can use dot notation for nested access
                (e.g., "user.profile.name" to create nested structure)
            result_path: Optional attribute path to extract from the result
                (e.g., "address.city" to extract a nested field from the result)
            
        Returns:
            WorkflowBuilder: The parent workflow builder for further configuration
            
        Raises:
            TaskConfigurationError: If required components are missing
            
        Examples:
            # Store the entire result at the "result" key
            task.output("result")
            
            # Store just the "value" field from the result at the "result_value" key
            task.output("result_value", "value")
            
            # Store the result at a nested location in the context
            task.output("user.details.account", "account_info")
        """
        # Set the result configuration
        self._task_def.result_key = context_key
        self._task_def.result_path = result_path
        
        # Validate the task definition
        TaskValidator.validate_task_definition(self._task_def)
        
        # Create a ProcessingTask
        task = ProcessingTask(
            name=self._task_def.name, 
            description=self._task_def.description, 
            input_model=self._task_def.input_model, 
            output_model=self._task_def.output_model,
            progress_model=self._task_def.progress_model,
            processor_function=self._task_def.processor_function
        )
        
        # Create the result mapping
        result_mapping = ResultMapping(context_key, result_path)

        # Add task to workflow
        self._wb.workflow.add_task(
            task=task,
            argument_mappings=self._task_def.argument_mappings,
            result_mapping=result_mapping
        )
        
        return self._wb 