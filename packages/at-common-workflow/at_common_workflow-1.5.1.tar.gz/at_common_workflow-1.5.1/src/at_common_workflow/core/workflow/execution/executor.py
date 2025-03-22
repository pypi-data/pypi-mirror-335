from typing import Set, AsyncIterator, List
import asyncio
import logging
from at_common_workflow.core.workflow.node import Node
from at_common_workflow.core.constants import TaskStatus, WorkflowEventType
from at_common_workflow.core.context import Context
from at_common_workflow.core.workflow.graph.dependency import DependencyManager
from .events import WorkflowEvent
from .progress import Progress

class WorkflowExecutor:
    """Handles the execution of tasks in a workflow."""
    
    def __init__(self, 
                 nodes: List[Node], 
                 context: Context, 
                 progress: Progress, 
                 dependency_manager: DependencyManager,
                 logger: logging.Logger):
        self.nodes = nodes
        self.context = context
        self.progress = progress
        self.dependency_manager = dependency_manager
        self.logger = logger
    
    def _get_ready_tasks(self, completed_tasks: Set[str]) -> Set[str]:
        """
        Get all tasks that are ready to be executed based on dependencies.
        
        Args:
            completed_tasks: Set of task names that have already been completed
            
        Returns:
            Set of task names that are ready to be executed
        """
        ready_tasks = set()
        
        for node in self.nodes:
            task_name = node.task.name
            
            # Skip tasks that are already completed
            if task_name in completed_tasks:
                continue
                
            # Check if all dependencies are satisfied
            dependencies = self.dependency_manager.get_dependencies(task_name)
            if all(dep in completed_tasks for dep in dependencies):
                ready_tasks.add(task_name)
                
        return ready_tasks
    
    async def _execute_task(self, task_name: str) -> AsyncIterator[WorkflowEvent]:
        """Execute a single task and update its status."""
        node = next(t for t in self.nodes if t.task.name == task_name)
        
        self.logger.info(f"Starting task: {task_name}")
        self.progress.update_task_status(task_name, TaskStatus.RUNNING)           
        try:
            args = {
                name: mapping.resolve(self.context)
                for name, mapping in node.argument_mappings.items()
            }
            
            self.logger.debug(f"Task {task_name} arguments resolved: {args}")
            final_result = None
            
            # Execute the task and handle its result (either async iterator or direct result)
            result = await node.task(**args)
            
            # Check if the task's processor_function is expected to return a direct value or async iterator
            is_generator_result = False
            processor_function = node.task.processor_function
            # Check the return annotation to see if it's expected to return a generator
            if hasattr(processor_function, '__annotations__') and 'return' in processor_function.__annotations__:
                return_annotation = processor_function.__annotations__['return']
                is_generator_result = 'AsyncIterator' in str(return_annotation) or 'AsyncGenerator' in str(return_annotation)
            
            # Check if result is an async iterator (progress events) or direct result
            if hasattr(result, '__aiter__'):
                # Handle async iterator result (progress events + final result)
                async for data in result:
                    # Store the latest data for final result
                    final_result = data
                    
                    # Only emit progress events if:
                    # 1. The original function was expected to return an async iterator (not a direct result)
                    # 2. And the data is either a progress model or not an output model
                    if is_generator_result:
                        is_progress_event = False
                        
                        if node.task.progress_model and isinstance(data, node.task.progress_model):
                            # This is a progress model
                            is_progress_event = True
                        elif not isinstance(data, node.task.output_model):
                            # This is not an output model
                            is_progress_event = True
                            
                        if is_progress_event:
                            # Emit progress event
                            yield WorkflowEvent(
                                WorkflowEventType.TASK_PROGRESS,
                                task_name=task_name,
                                task_data=data
                            )
            else:
                # Direct result with no progress events
                final_result = result
            
            # Store the final result
            if final_result is not None:
                node.result_mapping.store(self.context, final_result)
            else:
                # Handle the case where no data was yielded or returned
                self.logger.warning(f"Task {task_name} did not produce any data")
                # We could store a default value here if needed
            
            self.logger.info(f"Task completed successfully: {task_name}")
            self.progress.update_task_status(task_name, TaskStatus.COMPLETED)
        except Exception as e:
            self.logger.error(f"Task failed: {task_name}", exc_info=True)
            self.progress.update_task_status(task_name, TaskStatus.FAILED)
            yield WorkflowEvent(WorkflowEventType.TASK_FAILED, task_name=task_name, error=e)
            raise
    
    async def execute(self) -> AsyncIterator[WorkflowEvent]:
        """
        Execute tasks in parallel when possible based on their dependencies.
        Yields workflow events during execution.
        """
        self.logger.info("Starting workflow execution")
        yield WorkflowEvent(WorkflowEventType.WORKFLOW_STARTED)
        
        try:
            completed_tasks: Set[str] = set()
            tasks_in_progress = set()
            task_to_future = {}  # Maps task_name to its running future
            
            while len(completed_tasks) < len(self.nodes):
                ready_tasks = self._get_ready_tasks(completed_tasks) - tasks_in_progress
                
                if not ready_tasks and not tasks_in_progress:
                    remaining = {t.task.name for t in self.nodes} - completed_tasks
                    msg = f"Unable to make progress. Tasks stuck: {remaining}"
                    self.logger.error(msg)
                    raise RuntimeError(msg)
                
                if ready_tasks:
                    self.logger.debug(f"Starting new tasks: {ready_tasks}")
                
                # Start new tasks
                for task_name in ready_tasks:
                    # Create a queue for real-time event forwarding
                    event_queue = asyncio.Queue()
                    
                    # Create and start the task execution coroutine
                    async def execute_and_forward_events(task_name: str, queue: asyncio.Queue):
                        try:
                            async for event in self._execute_task(task_name):
                                await queue.put(("event", event))
                            # Signal task completion
                            await queue.put(("done", None))
                        except Exception as e:
                            # Signal task failure with the exception
                            self.logger.error(f"Task execution failed: {task_name}", exc_info=True)
                            await queue.put(("error", e))
                            # We don't re-raise here to prevent the task from crashing
                            # The error will be handled in the main execution loop
                    
                    # Start the task execution
                    task_future = asyncio.create_task(execute_and_forward_events(task_name, event_queue))
                    task_to_future[task_name] = (task_future, event_queue)
                    tasks_in_progress.add(task_name)
                    yield WorkflowEvent(WorkflowEventType.TASK_STARTED, task_name=task_name)
                
                # Process events from all running tasks
                if tasks_in_progress:
                    # Create a list of tasks to wait for events from all running tasks
                    event_wait_tasks = []
                    task_to_wait_task = {}  # Maps wait task to task_name
                    
                    for task_name in list(tasks_in_progress):
                        _, queue = task_to_future[task_name]
                        wait_task = asyncio.create_task(queue.get())
                        event_wait_tasks.append(wait_task)
                        task_to_wait_task[wait_task] = task_name
                    
                    # Wait for any task to produce an event
                    done, pending = await asyncio.wait(
                        event_wait_tasks, 
                        return_when=asyncio.FIRST_COMPLETED,
                        timeout=120  # Add a timeout to prevent hanging if a task gets stuck
                    )
                    
                    # If we timed out and no tasks completed, log a warning
                    if not done:
                        self.logger.warning("No events received from tasks within timeout period. Tasks may be stuck.")
                        continue
                    
                    # Cancel pending wait tasks (we'll recreate them in the next loop iteration)
                    for task in pending:
                        task.cancel()
                    
                    # Process completed event wait tasks
                    for wait_task in done:
                        event_type, event_data = await wait_task
                        task_name = task_to_wait_task[wait_task]
                        
                        if event_type == "event":
                            # Forward the event
                            yield event_data
                        elif event_type == "done":
                            # Task completed successfully
                            completed_tasks.add(task_name)
                            tasks_in_progress.remove(task_name)
                            del task_to_future[task_name]
                            yield WorkflowEvent(WorkflowEventType.TASK_COMPLETED, task_name=task_name)
                            self.logger.debug(f"Task completed and removed from in-progress: {task_name}")
                        elif event_type == "error":
                            # Task failed
                            self.logger.error(f"Task {task_name} failed: {event_data}")
                            tasks_in_progress.remove(task_name)
                            del task_to_future[task_name]
                            # The error event was already yielded by _execute_task
                            # Mark the workflow as failed if we're not continuing on failure
                            # Note: In a real implementation, you might want to add a configuration option
                            # to control whether to continue execution when a task fails
                            raise RuntimeError(f"Workflow execution failed due to task failure: {task_name}")
            
            self.logger.info("Workflow execution completed successfully")
            yield WorkflowEvent(WorkflowEventType.WORKFLOW_COMPLETED)
            
        except Exception as e:
            self.logger.error("Workflow execution failed", exc_info=True)
            yield WorkflowEvent(WorkflowEventType.WORKFLOW_FAILED, error=e)
            raise