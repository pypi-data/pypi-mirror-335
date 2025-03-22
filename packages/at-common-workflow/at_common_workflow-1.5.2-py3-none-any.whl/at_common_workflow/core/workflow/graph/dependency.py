from typing import Dict, Set, List, Optional
from at_common_workflow.core.workflow.node import Node
from at_common_workflow.core.exceptions import DependencyError, format_error

class DependencyManager:
    """Manages task dependencies in a workflow."""
    
    def __init__(self):
        self._task_dependencies: Dict[str, Set[str]] = {}
        self._reverse_dependencies: Dict[str, Set[str]] = {}
        
    def initialize(self, nodes: List[Node]) -> None:
        """Initialize dependency dictionaries for all tasks."""
        self._task_dependencies.clear()
        self._reverse_dependencies.clear()
        for node in nodes:
            task_name = node.task.name
            self._task_dependencies[task_name] = set()
            self._reverse_dependencies[task_name] = set()
    
    def add_dependency(self, dependent: str, provider: str) -> None:
        """Add a dependency between tasks."""
        if dependent == provider:
            raise DependencyError(format_error(
                "Task cannot depend on itself", 
                task_name=dependent
            ))
        self._task_dependencies[dependent].add(provider)
        self._reverse_dependencies[provider].add(dependent)
    
    def get_dependencies(self, task_name: str) -> Set[str]:
        """Get dependencies for a task."""
        return self._task_dependencies.get(task_name, set())
    
    def get_dependents(self, task_name: str) -> Set[str]:
        """Get tasks that depend on this task."""
        return self._reverse_dependencies.get(task_name, set())
    
    def has_cycle(self) -> bool:
        """
        Check for cycles in the dependency graph using DFS.
        
        Returns:
            bool: True if a cycle is detected, False otherwise
        """
        # States for DFS: 0 = unvisited, 1 = visiting, 2 = visited
        states: Dict[str, int] = {task: 0 for task in self._task_dependencies}
        
        def dfs(task: str) -> bool:
            # If we're already visiting this node, we found a cycle
            if states[task] == 1:
                return True
            # If we've already visited this node, no cycle here
            if states[task] == 2:
                return False
                
            # Mark as visiting
            states[task] = 1
            
            # Visit all dependencies
            for dep in self._task_dependencies[task]:
                if dfs(dep):
                    return True
                    
            # Mark as visited
            states[task] = 2
            return False
        
        # Try starting DFS from each node
        for task in self._task_dependencies:
            if states[task] == 0:  # Only start from unvisited nodes
                if dfs(task):
                    return True
                    
        return False
    
    def find_cycle_task(self) -> Optional[str]:
        """
        Find a task that is part of a cycle.
        
        Returns:
            Optional[str]: A task name that is part of a cycle, or None if no cycle exists
        """
        # States for DFS: 0 = unvisited, 1 = visiting, 2 = visited
        states: Dict[str, int] = {task: 0 for task in self._task_dependencies}
        cycle_task = None
        
        def dfs(task: str) -> bool:
            nonlocal cycle_task
            # If we're already visiting this node, we found a cycle
            if states[task] == 1:
                cycle_task = task
                return True
            # If we've already visited this node, no cycle here
            if states[task] == 2:
                return False
                
            # Mark as visiting
            states[task] = 1
            
            # Visit all dependencies
            for dep in self._task_dependencies[task]:
                if dfs(dep):
                    return True
                    
            # Mark as visited
            states[task] = 2
            return False
        
        # Try starting DFS from each node
        for task in self._task_dependencies:
            if states[task] == 0:  # Only start from unvisited nodes
                if dfs(task):
                    return cycle_task
                    
        return None