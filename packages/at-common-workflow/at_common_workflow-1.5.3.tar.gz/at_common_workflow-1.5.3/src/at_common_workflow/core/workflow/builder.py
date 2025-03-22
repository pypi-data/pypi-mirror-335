import logging
from pathlib import Path
from typing import Optional, Dict
from at_common_workflow.core.task import TaskBuilder
from at_common_workflow.utils.logging import setup_logging
from at_common_workflow.core.exceptions import WorkflowValidationError, format_error
from .base import Workflow

class WorkflowBuilder:
    """
    Builder for creating and configuring workflow DAGs.
    
    This builder provides a fluent interface for constructing workflows
    with proper dependency management and execution control.
    
    Example:
        workflow = (
            WorkflowBuilder()
            .task("add_numbers")
                .input_model(AddInputModel)
                .output_model(AddOutputModel)
                .processor(add_function)
                .arg("a", 5)
                .arg("b", from_ctx="x")
                .output("result")
            .task("multiply_numbers")
                .input_model(MultiplyInputModel)
                .output_model(MultiplyOutputModel)
                .processor(multiply_function)
                .arg("a", from_ctx="result")
                .arg("b", 2)
                .output("final_result")
            .build()
        )
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None, strict_validation: bool = False):
        """
        Initialize a workflow builder.
        
        Args:
            logger: Optional logger to use for workflow logging
            strict_validation: If True, validates that all referenced context keys are provided.
                              Default is False since most keys are provided at runtime.
        """
        self.workflow = Workflow(logger=logger, strict_validation=strict_validation)
        # We'll keep track of task names but not enforce uniqueness
        self._task_names: Dict[str, int] = {}
    
    def configure_logging(self, 
        level: int = logging.INFO,
        log_file: Optional[Path] = None,
        format_string: Optional[str] = None
    ) -> 'WorkflowBuilder':
        """
        Configure logging for this workflow builder.
        
        Sets up appropriate logging for the workflow builder and its workflow.
        
        Args:
            level: Logging level (default: INFO)
            log_file: Optional path to log file for persistent logging
            format_string: Optional custom format string for log messages
            
        Returns:
            WorkflowBuilder: Self for method chaining
        """
        logger = setup_logging(level, log_file, format_string)
        self.workflow.logger = logger
        return self

    def task(self, name: str) -> TaskBuilder:
        """
        Define a new task in the workflow.
        
        Creates a task with the given name and returns a builder
        for configuring its inputs, outputs, and execution logic.
        
        Args:
            name: Name for the task (doesn't need to be globally unique)
            
        Returns:
            TaskBuilder: Builder for configuring the task
            
        Raises:
            WorkflowValidationError: If name is empty or None
            
        Example:
            workflow_builder.task("add_numbers")
                .input_model(AddInputModel)
                .output_model(AddOutputModel)
                .processor(add_function)
                .arg("a", 5)
                .output("result")
        """
        if not name:
            raise WorkflowValidationError(format_error("Task name cannot be empty"))
            
        # Track task names for debugging but allow duplicates
        self._task_names[name] = self._task_names.get(name, 0) + 1
            
        return TaskBuilder(self, name=name)

    def build(self) -> Workflow:
        """
        Build and validate the workflow.
        
        Validates the workflow configuration including dependency
        resolution and cycle detection.
        
        Returns:
            Workflow: The built and validated workflow, ready for execution
        
        Raises:
            WorkflowValidationError: If the workflow has validation errors (cycles, missing dependencies)
        """
        # Validate the workflow before returning it
        try:
            self.workflow._build_dependency_graph()
        except Exception as e:
            raise WorkflowValidationError(format_error(f"Workflow validation failed: {str(e)}")) from e
            
        return self.workflow