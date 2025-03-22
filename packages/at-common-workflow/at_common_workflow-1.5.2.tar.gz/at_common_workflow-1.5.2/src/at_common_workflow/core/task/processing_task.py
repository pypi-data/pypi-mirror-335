from typing import Type, Any, Callable, AsyncIterator, Awaitable, Dict, Optional, Union, TypeVar, Generic, cast
from .base import BaseTask, InputType, OutputType
from .validation import validate_task_configuration, validate_input, validate_output
from at_common_workflow.core.exceptions import TaskExecutionError, ModelValidationError

ProgressType = TypeVar('ProgressType')

class ProcessingTask(BaseTask[InputType, OutputType], Generic[InputType, OutputType, ProgressType]):
    """
    Represents a processing task in a workflow with typed input and output.
    
    A processing task:
    - Accepts input conforming to a Pydantic model
    - Processes that input according to business logic
    - Produces output conforming to a Pydantic model
    - Can optionally emit progress events during processing
    """
    
    def __init__(
        self, 
        name: str,
        description: Optional[str] = None,
        input_model: Optional[Type[InputType]] = None,
        output_model: Optional[Type[OutputType]] = None,
        progress_model: Optional[Type[ProgressType]] = None,
        processor_function: Optional[Callable[[InputType], Union[Awaitable[OutputType], Awaitable[AsyncIterator[Union[ProgressType, OutputType]]]]]] = None
    ):
        """
        Initialize a processing task with its configuration.
        
        Args:
            name: Unique task name
            description: Optional task description
            input_model: Pydantic model class for input validation
            output_model: Pydantic model class for output validation
            progress_model: Optional Pydantic model class for progress events validation
            processor_function: Async function that executes the task logic.
                         Can either return a final result or an async iterator
                         for emitting progress events and the final result.
        """
        super().__init__(name, description)
        self.input_model = input_model
        self.output_model = output_model
        self.progress_model = progress_model or output_model
        self.processor_function = processor_function
        self._validate()
        
    def _validate(self) -> None:
        """Validate that task configuration is properly defined."""
        validate_task_configuration(
            self.name,
            self.input_model,
            self.output_model,
            self.progress_model,
            self.processor_function
        )
    
    def __repr__(self) -> str:
        """String representation of the task."""
        return f"{self.__class__.__name__}(name={self.name!r}, description={self.description!r}) {self.input_model.__name__} -> {self.output_model.__name__}"
    
    async def _create_validated_stream(
        self, 
        result_gen: Optional[AsyncIterator[Union[ProgressType, OutputType]]], 
        final_result: Optional[OutputType] = None
    ) -> AsyncIterator[Union[ProgressType, OutputType]]:
        """
        Create a validated output stream from the result generator.
        If final_result is provided, it will be emitted as the last item of the stream.
        
        Args:
            result_gen: Async iterator of results
            final_result: Optional final result to emit at the end
            
        Returns:
            Async iterator of validated results
            
        Raises:
            ModelValidationError: If validation fails
        """
        if result_gen is not None:
            try:
                async for item in result_gen:
                    # Determine if this is a progress event or final result
                    # If it's the output model type or if we can't determine, assume it's the output
                    is_progress = (self.progress_model and 
                                  isinstance(item, self.progress_model) and 
                                  not isinstance(item, self.output_model))
                    
                    # Validate based on the determined type
                    yield validate_output(
                        self.name,
                        item,
                        self.output_model,
                        self.progress_model,
                        is_progress=is_progress
                    )
            except Exception as e:
                # Just re-raise ModelValidationError, otherwise wrap it
                if isinstance(e, ModelValidationError):
                    raise
                raise ModelValidationError(f"Stream validation failed in task '{self.name}': {str(e)}") from e
        
        if final_result is not None:
            # Emit the final result with proper validation
            yield validate_output(
                self.name,
                final_result,
                self.output_model,
                self.progress_model,
                is_progress=False
            )
    
    async def __call__(self, **kwargs) -> AsyncIterator[Union[ProgressType, OutputType]]:
        """
        Allow tasks to be called directly for testing/debugging.
        Validates both input and output.
        
        Args:
            **kwargs: Input arguments
            
        Returns:
            An async iterator of validated outputs and optional progress events
            
        Raises:
            ModelValidationError: If input or output validation fails
            TaskExecutionError: Any exception raised during task execution
            Exception: Other exceptions
        """
        if not self.processor_function:
            raise TaskExecutionError(f"No processor function defined for task '{self.name}'")
            
        # Validate input
        input_model = validate_input(self.name, self.input_model, **kwargs)
        
        try:
            # Execute the function and handle different return types
            result = self.processor_function(input_model)
            
            # Check if it returns an async generator
            if hasattr(result, '__aiter__'):
                # Result is already an AsyncIterator, use it directly
                async_iter = cast(AsyncIterator[Union[ProgressType, OutputType]], result)
                # Don't use await here as _create_validated_stream returns an AsyncIterator
                return self._create_validated_stream(async_iter)
            else:
                # Result is likely an awaitable that will resolve to a final value
                # Wait for the final result
                final_result = await cast(Awaitable[OutputType], result)
                # Convert to stream with just one item
                return self._create_validated_stream(None, final_result=final_result)
                
        except Exception as e:
            # Re-raise validation errors directly
            if isinstance(e, (ModelValidationError, TaskExecutionError)):
                raise
            # Wrap other errors as task execution errors
            raise TaskExecutionError(f"Execution failed in task '{self.name}': {str(e)}") from e