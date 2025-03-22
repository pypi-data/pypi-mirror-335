from typing import List, Dict, Optional, AsyncIterator, Set, cast, Any
import logging
from at_common_workflow.core.context import Context
from at_common_workflow.core.task import ProcessingTask
from at_common_workflow.utils import ArgumentMapping, ResultMapping
from at_common_workflow.utils.logging import setup_logging
from at_common_workflow.core.exceptions import WorkflowValidationError, format_error
from .node import Node
from .execution.progress import Progress
from .graph.dependency import DependencyManager
from .execution.executor import WorkflowExecutor
from .execution.events import WorkflowEvent
from at_common_workflow.core.constants import WorkflowEventType

class Workflow:
    """
    Orchestrates the execution of tasks in a directed acyclic graph (DAG) with parallel execution support.
    
    Features:
    - Automatic dependency resolution based on input/output relationships
    - Concurrent execution of independent tasks
    - Progress tracking during execution
    - Comprehensive logging
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None, strict_validation: bool = True):
        """
        Initialize a workflow.
        
        Args:
            logger: Optional logger for workflow execution logging
            strict_validation: If True, all referenced context keys must be provided by tasks
        """
        self.nodes: List[Node] = []
        self.context = Context()
        self.progress = Progress()
        self.dependency_manager = DependencyManager()
        self.logger = logger or setup_logging()
        self.strict_validation = strict_validation
    
    def add_task(
        self,
        task: ProcessingTask,
        argument_mappings: Dict[str, ArgumentMapping],
        result_mapping: ResultMapping
    ) -> None:
        """
        Add a task to the workflow with its input arguments and output destination.
        
        Args:
            task: The task to add to the workflow
            argument_mappings: Dict mapping argument names to sources (constant values or context references)
            result_mapping: Specification of where to store the task's result in the context
            
        Raises:
            WorkflowValidationError: If task or mappings are invalid
        """           
        if not task:
            raise WorkflowValidationError(format_error("Task cannot be None"))
            
        if not isinstance(argument_mappings, dict):
            raise WorkflowValidationError(format_error("Argument mappings must be a dictionary"))
            
        if not result_mapping:
            raise WorkflowValidationError(format_error("Result mapping cannot be None"))
            
        node = Node(task, argument_mappings, result_mapping)
        self.nodes.append(node)
    
    def _collect_context_providers_and_references(self) -> tuple[Dict[str, str], Set[str]]:
        """
        Collect context providers and references from the workflow.
        
        Returns:
            Tuple containing:
            - Dict mapping context keys to task names that provide them
            - Set of all context keys referenced by tasks
        """
        # First pass: collect all context providers and referenced keys
        context_providers: Dict[str, str] = {}  # Maps context_key -> task_name
        referenced_keys: Set[str] = set()
        
        for node in self.nodes:
            task_name = node.task.name
            
            # Record this task as the provider for its result key
            context_key = node.result_mapping.context_key
            context_providers[context_key] = task_name
            
            # Also register the task as a provider for all parent paths
            # E.g., if a task provides 'math.operations.addition', it should also be 
            # registered as providing 'math.operations' and 'math' for dependency tracking
            if '.' in context_key:
                parts = context_key.split('.')
                for i in range(1, len(parts)):
                    parent_key = '.'.join(parts[:i])
                    # Only register if not already registered by another task
                    if parent_key not in context_providers:
                        context_providers[parent_key] = task_name
            
            # Collect all context keys referenced by this task's arguments
            for _, arg_mapping in node.argument_mappings.items():
                referenced_keys.update(arg_mapping.get_context_refs())
                
        return context_providers, referenced_keys
    
    def _validate_references(self, referenced_keys: Set[str], context_providers: Dict[str, str]) -> None:
        """
        Validate that referenced keys exist or will be created by a task.
        
        Args:
            referenced_keys: Set of all context keys referenced by tasks
            context_providers: Dict mapping context keys to task names that provide them
            
        Raises:
            WorkflowValidationError: If a task references a key that is not provided by any task (only when strict_validation is True)
        """
        # Skip validation if not in strict mode
        if not self.strict_validation:
            return
            
        missing_keys = []
        for key in referenced_keys:
            # If the key is already in the context, it's fine
            if key in self.context:
                continue
                
            # If no task provides this key
            if key not in context_providers:
                missing_keys.append(key)
                
        if missing_keys:
            raise WorkflowValidationError(
                format_error(f"The following context keys are referenced but not provided: {', '.join(missing_keys)}")
            )
    
    def _create_dependencies(self, context_providers: Dict[str, str]) -> None:
        """
        Create task dependencies based on context references.
        
        Args:
            context_providers: Dict mapping context keys to task names that provide them
        """
        for node in self.nodes:
            task_name = node.task.name

            # Check context references in arguments
            for _, arg_mapping in node.argument_mappings.items():
                for context_key in arg_mapping.get_context_refs():
                    if context_key in context_providers:
                        provider_task = context_providers[context_key]
                        if provider_task != task_name:  # Avoid self-dependencies
                            self.dependency_manager.add_dependency(task_name, provider_task)
    
    def _build_dependency_graph(self) -> None:
        """
        Build the dependency graph based on context references.
        
        Raises:
            WorkflowValidationError: If there are cycles or undefined references
        """
        # First pass: collect all context providers and referenced keys
        context_providers, referenced_keys = self._collect_context_providers_and_references()

        # Check for references to undefined keys
        self._validate_references(referenced_keys, context_providers)

        # Initialize dependency manager
        self.dependency_manager.initialize(self.nodes)

        # Second pass: build dependencies based on context references
        self._create_dependencies(context_providers)

        # Check for cycles in the dependency graph
        if self.dependency_manager.has_cycle():
            cycle_task = self.dependency_manager.find_cycle_task()
            raise WorkflowValidationError(
                format_error(
                    f"Cyclic dependencies detected: task '{cycle_task}' is part of a cycle. "
                    f"This means a task depends directly or indirectly on its own output."
                )
            )

    async def execute(self, initial_context: Optional['Context'] = None) -> AsyncIterator[WorkflowEvent]:
        """
        Execute tasks in parallel when possible based on their dependencies.
        
        Executes the workflow by running tasks in parallel when their dependencies
        are satisfied. Progress and results are stored in the context.
        
        Args:
            initial_context: Optional initial context with input values
            
        Yields:
            WorkflowEvent: Events during workflow execution (start, progress, completion, or failure)
        
        Raises:
            WorkflowValidationError: If the workflow configuration is invalid
            Exception: Any exception that occurs during task execution
        """
        try:
            self._build_dependency_graph()
            self.logger.debug("Dependency graph built successfully")
            
            # Update context with initial values if provided
            if initial_context:
                self.context.update(initial_context)
            
            executor = WorkflowExecutor(
                nodes=self.nodes,
                context=self.context,
                progress=self.progress,
                dependency_manager=self.dependency_manager,
                logger=self.logger
            )
            
            async for event in executor.execute():
                yield event
                
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
            yield WorkflowEvent(WorkflowEventType.WORKFLOW_FAILED, error=e)
            raise