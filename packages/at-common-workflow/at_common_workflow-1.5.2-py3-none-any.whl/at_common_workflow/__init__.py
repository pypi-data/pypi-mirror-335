"""
AT Common Workflow - A DAG-based workflow execution engine with typed input/output.

This package provides a framework for defining and executing workflows
with automatic dependency resolution, parallel execution, and progress tracking.
"""

# Core components
from at_common_workflow.core.context import Context
from at_common_workflow.core.task.processing_task import ProcessingTask
from at_common_workflow.core.workflow.base import Workflow
from at_common_workflow.core.workflow.builder import WorkflowBuilder

# Constants and types
from at_common_workflow.core.constants import WorkflowEventType
from at_common_workflow.core.task.base import InputType, OutputType

__version__ = "1.5.0"
__all__ = [
    # Core components
    "Context",
    "ProcessingTask",
    "Workflow",
    "WorkflowBuilder",
    
    # Constants and types
    "WorkflowEventType",
    "InputType", 
    "OutputType"
]