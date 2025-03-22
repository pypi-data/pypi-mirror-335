from typing import Dict, Set, Optional
from at_common_workflow.core.task import ProcessingTask
from at_common_workflow.utils import ArgumentMapping, ResultMapping
from at_common_workflow.core.exceptions import TaskValidationError, WorkflowValidationError, format_error
from at_common_workflow.core.task.validation import validate_arguments

class Node:
    """Represents a task node in the workflow graph."""
    
    def __init__(
        self,
        task: ProcessingTask,
        argument_mappings: Dict[str, ArgumentMapping],
        result_mapping: ResultMapping
    ) -> None:
        """
        Initialize a workflow node.
        
        Args:
            task: The task to execute
            argument_mappings: Mappings for task arguments
            result_mapping: Mapping for task result
            
        Raises:
            TaskValidationError: If argument validation fails
            WorkflowValidationError: If task or result_mapping is None
        """
        if not task:
            raise WorkflowValidationError(format_error("Task cannot be None"))
        if not result_mapping:
            raise WorkflowValidationError(format_error("Result mapping cannot be None"))
            
        # Validate arguments against the input model
        validate_arguments(task.name, task.input_model, argument_mappings)
        
        self.task = task
        self.argument_mappings = argument_mappings
        self.result_mapping = result_mapping
        self.dependencies: Set[str] = set()
    
    def __repr__(self) -> str:
        """String representation of the node."""
        return f"Node(task={self.task.name}, result_key={self.result_mapping.context_key})"