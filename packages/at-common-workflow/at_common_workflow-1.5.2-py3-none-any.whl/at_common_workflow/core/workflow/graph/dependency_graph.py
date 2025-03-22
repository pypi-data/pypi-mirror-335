from typing import Dict, Set, List, Optional, Tuple, Iterator
from at_common_workflow.core.workflow.node import Node
from at_common_workflow.core.exceptions import DependencyError, WorkflowValidationError, format_error

class DependencyGraph:
    """
    Represents a dependency graph of tasks in a workflow.
    
    This class provides a more robust interface for managing task dependencies,
    including operations for adding, validating, and querying dependencies.
    It serves as an abstraction layer over the basic dependency management.
    """
    
    def __init__(self):
        """Initialize an empty dependency graph."""
        # Forward dependencies: task -> tasks it depends on
        self._dependencies: Dict[str, Set[str]] = {}
        
        # Reverse dependencies: task -> tasks that depend on it
        self._dependents: Dict[str, Set[str]] = {}
        
        # Tasks in topological order (if acyclic)
        self._execution_order: List[str] = []
        
        # Cache for cycle detection
        self._has_cycles: Optional[bool] = None
        self._cycle_task: Optional[str] = None
    
    def initialize(self, tasks: List[str]) -> None:
        """
        Initialize the graph with a set of tasks.
        
        Args:
            tasks: List of task names to initialize the graph with
        """
        self._dependencies.clear()
        self._dependents.clear()
        self._execution_order.clear()
        self._has_cycles = None
        self._cycle_task = None
        
        for task in tasks:
            self._dependencies[task] = set()
            self._dependents[task] = set()
    
    def add_dependency(self, dependent: str, provider: str) -> None:
        """
        Add a dependency between tasks.
        
        Args:
            dependent: The task that depends on the provider
            provider: The task that the dependent depends on
            
        Raises:
            DependencyError: If a task depends on itself
        """
        # Validation
        if dependent == provider:
            raise DependencyError(format_error(
                "Task cannot depend on itself", 
                task_name=dependent
            ))
        
        # Already recorded this dependency
        if provider in self._dependencies[dependent]:
            return
            
        # Add the dependency
        self._dependencies[dependent].add(provider)
        self._dependents[provider].add(dependent)
        
        # Invalidate cached values
        self._has_cycles = None
        self._cycle_task = None
        self._execution_order.clear()
    
    def get_dependencies(self, task: str) -> Set[str]:
        """
        Get all tasks that this task depends on.
        
        Args:
            task: The task to get dependencies for
            
        Returns:
            Set of task names that this task depends on
        """
        return self._dependencies.get(task, set()).copy()
    
    def get_dependents(self, task: str) -> Set[str]:
        """
        Get all tasks that depend on this task.
        
        Args:
            task: The task to get dependents for
            
        Returns:
            Set of task names that depend on this task
        """
        return self._dependents.get(task, set()).copy()
    
    def get_all_tasks(self) -> Set[str]:
        """
        Get all tasks in the graph.
        
        Returns:
            Set of all task names in the graph
        """
        return set(self._dependencies.keys())
    
    def has_cycles(self) -> bool:
        """
        Check if the graph has any cycles.
        
        Returns:
            True if the graph has cycles, False otherwise
        """
        if self._has_cycles is not None:
            return self._has_cycles
            
        # Cache miss, run the detection
        visited = {task: 0 for task in self._dependencies}  # 0 = unvisited, 1 = visiting, 2 = visited
        
        def dfs(task: str) -> bool:
            if visited[task] == 1:  # Currently visiting - cycle found
                self._cycle_task = task
                return True
            if visited[task] == 2:  # Already visited - no cycle
                return False
                
            visited[task] = 1  # Mark as visiting
            
            # Visit dependencies
            for dep in self._dependencies[task]:
                if dfs(dep):
                    return True
                    
            visited[task] = 2  # Mark as visited
            return False
        
        # Run DFS from each unvisited node
        for task in self._dependencies:
            if visited[task] == 0 and dfs(task):
                self._has_cycles = True
                return True
                
        # No cycles found
        self._has_cycles = False
        return False
    
    def get_cycle_task(self) -> Optional[str]:
        """
        Get a task that is part of a cycle, if one exists.
        
        Returns:
            A task name that is part of a cycle, or None if no cycles exist
        """
        if not self.has_cycles():
            return None
        return self._cycle_task
    
    def validate(self) -> None:
        """
        Validate the dependency graph.
        
        Raises:
            WorkflowValidationError: If the graph has cycles
        """
        if self.has_cycles():
            cycle_task = self.get_cycle_task()
            raise WorkflowValidationError(
                format_error(
                    f"Cyclic dependencies detected: task '{cycle_task}' is part of a cycle. "
                    f"This means a task depends directly or indirectly on its own output."
                )
            )
    
    def get_execution_order(self) -> List[str]:
        """
        Get a valid execution order for tasks (topological sort).
        
        Returns:
            List of task names in a valid execution order
            
        Raises:
            WorkflowValidationError: If the graph has cycles
        """
        if self._execution_order:
            return self._execution_order.copy()
            
        # Check for cycles first
        self.validate()
        
        # Compute topological sort
        visited = {task: False for task in self._dependencies}
        order = []
        
        def visit(task: str) -> None:
            if visited[task]:
                return
                
            visited[task] = True
            
            # Visit dependencies first
            for dep in self._dependencies[task]:
                visit(dep)
                
            # Add this task to the order
            order.append(task)
        
        # Visit all tasks
        for task in self._dependencies:
            if not visited[task]:
                visit(task)
                
        # Reverse to get correct order (dependencies before dependents)
        self._execution_order = list(reversed(order))
        return self._execution_order.copy()
    
    def get_ready_tasks(self, completed_tasks: Set[str]) -> Set[str]:
        """
        Get all tasks that are ready to be executed.
        
        A task is ready if all its dependencies have been completed.
        
        Args:
            completed_tasks: Set of tasks that have already been completed
            
        Returns:
            Set of task names that are ready to be executed
        """
        ready = set()
        for task in self._dependencies:
            if task in completed_tasks:
                continue
                
            if all(dep in completed_tasks for dep in self._dependencies[task]):
                ready.add(task)
                
        return ready 