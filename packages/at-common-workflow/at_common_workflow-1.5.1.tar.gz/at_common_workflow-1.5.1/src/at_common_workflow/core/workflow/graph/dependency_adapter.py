from typing import Dict, Set, List, Optional
from at_common_workflow.core.workflow.node import Node
from at_common_workflow.core.exceptions import DependencyError, format_error
from at_common_workflow.core.workflow.graph.dependency_graph import DependencyGraph

class DependencyAdapter:
    """
    Adapter class that provides the old DependencyManager interface while using the new DependencyGraph.
    
    This class allows for a gradual transition from the old dependency management to the new one
    without breaking existing code. It delegates all operations to the new DependencyGraph class.
    """
    
    def __init__(self):
        """Initialize a dependency adapter."""
        self._graph = DependencyGraph()
        
    def initialize(self, nodes: List[Node]) -> None:
        """
        Initialize dependency dictionaries for all tasks.
        
        Args:
            nodes: List of nodes to initialize dependencies for
        """
        task_names = [node.task.name for node in nodes]
        self._graph.initialize(task_names)
    
    def add_dependency(self, dependent: str, provider: str) -> None:
        """
        Add a dependency between tasks.
        
        Args:
            dependent: The task that depends on the provider
            provider: The task that the dependent depends on
            
        Raises:
            DependencyError: If a task depends on itself
        """
        self._graph.add_dependency(dependent, provider)
    
    def get_dependencies(self, task_name: str) -> Set[str]:
        """
        Get dependencies for a task.
        
        Args:
            task_name: The task to get dependencies for
            
        Returns:
            Set of task names that this task depends on
        """
        return self._graph.get_dependencies(task_name)
    
    def get_dependents(self, task_name: str) -> Set[str]:
        """
        Get tasks that depend on this task.
        
        Args:
            task_name: The task to get dependents for
            
        Returns:
            Set of task names that depend on this task
        """
        return self._graph.get_dependents(task_name)
    
    def has_cycle(self) -> bool:
        """
        Check for cycles in the dependency graph.
        
        Returns:
            bool: True if a cycle is detected, False otherwise
        """
        return self._graph.has_cycles()
    
    def find_cycle_task(self) -> Optional[str]:
        """
        Find a task that is part of a cycle.
        
        Returns:
            Optional[str]: A task name that is part of a cycle, or None if no cycle exists
        """
        return self._graph.get_cycle_task()
    
    # New methods that provide enhanced functionality
    
    def validate(self) -> None:
        """
        Validate the dependency graph.
        
        Raises:
            WorkflowValidationError: If the graph has cycles
        """
        self._graph.validate()
    
    def get_execution_order(self) -> List[str]:
        """
        Get a valid execution order for tasks.
        
        Returns:
            List of task names in a valid execution order
            
        Raises:
            WorkflowValidationError: If the graph has cycles
        """
        return self._graph.get_execution_order()
    
    def get_ready_tasks(self, completed_tasks: Set[str]) -> Set[str]:
        """
        Get tasks that are ready to be executed.
        
        Args:
            completed_tasks: Set of tasks that have been completed
            
        Returns:
            Set of tasks that are ready to be executed
        """
        return self._graph.get_ready_tasks(completed_tasks) 