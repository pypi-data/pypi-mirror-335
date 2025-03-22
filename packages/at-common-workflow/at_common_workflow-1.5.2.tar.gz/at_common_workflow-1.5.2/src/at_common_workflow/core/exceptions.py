class WorkflowError(Exception):
    """Base exception for workflow-related errors"""
    pass

class TaskValidationError(WorkflowError):
    """Raised when task validation fails"""
    pass

class WorkflowValidationError(WorkflowError):
    """Raised when workflow validation fails"""
    pass

class TaskConfigurationError(WorkflowError):
    """Raised when task configuration is invalid"""
    pass

class ModelValidationError(WorkflowError):
    """Raised when input or output model validation fails"""
    pass

class TaskExecutionError(WorkflowError):
    """Raised when task execution fails"""
    pass

class DependencyError(WorkflowError):
    """Raised when there's an issue with task dependencies"""
    pass

class ContextError(WorkflowError):
    """Raised when there's an issue with the context"""
    pass

def format_error(base_message: str, task_name: str = None, details: str = None) -> str:
    """
    Format error messages consistently.
    
    Args:
        base_message: The main error message
        task_name: Optional task name for context
        details: Optional additional error details
        
    Returns:
        Formatted error message
    """
    parts = []
    
    if task_name:
        parts.append(f"Task '{task_name}':")
    
    parts.append(base_message)
    
    if details:
        parts.append(f"- {details}")
    
    return " ".join(parts)