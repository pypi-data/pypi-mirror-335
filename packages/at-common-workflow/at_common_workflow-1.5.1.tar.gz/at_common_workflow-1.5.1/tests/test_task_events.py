import pytest
import asyncio
import time
from typing import AsyncIterator, Optional, Union
from pydantic import BaseModel

from at_common_workflow.core.workflow.builder import WorkflowBuilder
from at_common_workflow.core.constants import WorkflowEventType


# Models for testing
class InputModel(BaseModel):
    count: int = 3
    should_emit_progress: bool = True
    delay: float = 0.1


class ResultModel(BaseModel):
    final_result: str
    execution_time: float


class ProgressModel(BaseModel):
    iteration: int
    percentage: float


@pytest.mark.asyncio
async def test_direct_result_task():
    """Test a task that returns a direct result without progress events."""
    
    async def direct_result_task(input: InputModel) -> ResultModel:
        """Task that returns a direct result without emitting progress events."""
        start_time = time.time()
        # Simulate work
        await asyncio.sleep(input.delay)
        execution_time = time.time() - start_time
        
        return ResultModel(
            final_result=f"Processed {input.count} items",
            execution_time=execution_time
        )
    
    workflow = (WorkflowBuilder()
        .task("direct_task")
            .input_model(InputModel)
            .output_model(ResultModel)
            .processor(direct_result_task)
            .arg("count", 5)
            .arg("should_emit_progress", False)
            .arg("delay", 0.01)
            .output("result")
        .build()
    )
    
    # Collect all events during execution
    events = []
    async for event in workflow.execute():
        events.append(event)
    
    # Verify we get started, completed but no progress events
    assert len(events) == 4  # WORKFLOW_STARTED, TASK_STARTED, TASK_COMPLETED, WORKFLOW_COMPLETED
    assert events[0].type == WorkflowEventType.WORKFLOW_STARTED
    assert events[1].type == WorkflowEventType.TASK_STARTED
    assert events[2].type == WorkflowEventType.TASK_COMPLETED
    assert events[3].type == WorkflowEventType.WORKFLOW_COMPLETED
    
    # Verify no progress events
    progress_events = [e for e in events if e.type == WorkflowEventType.TASK_PROGRESS]
    assert len(progress_events) == 0
    
    # Verify result is stored correctly
    result = workflow.context.get("result")
    assert result.final_result == "Processed 5 items"
    assert result.execution_time > 0


@pytest.mark.asyncio
async def test_progress_events_task():
    """Test a task that emits progress events and returns a final result."""
    
    async def progress_task(input: InputModel) -> AsyncIterator[Union[ProgressModel, ResultModel]]:
        """Task that emits progress events and a final result."""
        start_time = time.time()
        
        if input.should_emit_progress:
            # Emit progress events
            for i in range(input.count - 1):  # One less to keep space for final
                percentage = (i + 1) / input.count * 100
                # Clearly create a ProgressModel instance
                progress = ProgressModel(iteration=i+1, percentage=percentage)
                yield progress
                await asyncio.sleep(input.delay)
        
        # Calculate total execution time
        execution_time = time.time() - start_time
        
        # Clearly create a ResultModel instance for the final result
        final_result = ResultModel(
            final_result=f"Completed processing {input.count} items", 
            execution_time=execution_time
        )
        yield final_result
    
    workflow = (WorkflowBuilder()
        .task("progress_task")
            .input_model(InputModel)
            .output_model(ResultModel)
            .progress_model(ProgressModel)
            .processor(progress_task)
            .arg("count", 3)
            .arg("should_emit_progress", True)
            .arg("delay", 0.01)
            .output("result")
        .build()
    )
    
    # Collect all events during execution
    events = []
    async for event in workflow.execute():
        events.append(event)
    
    # Verify we get the right events
    assert len(events) == 6  # WORKFLOW_STARTED, TASK_STARTED, 2x TASK_PROGRESS, TASK_COMPLETED, WORKFLOW_COMPLETED
    assert events[0].type == WorkflowEventType.WORKFLOW_STARTED
    assert events[1].type == WorkflowEventType.TASK_STARTED
    
    # Get just the progress events
    progress_events = [e for e in events if e.type == WorkflowEventType.TASK_PROGRESS]
    assert len(progress_events) == 2
    
    # Check progress event data
    assert progress_events[0].task_data.iteration == 1
    assert abs(progress_events[0].task_data.percentage - 100/3) < 0.001
    assert progress_events[1].task_data.iteration == 2
    assert abs(progress_events[1].task_data.percentage - 200/3) < 0.001
    
    # Check timing of events - they should be spaced out by approximately the delay
    task_started_idx = next(i for i, e in enumerate(events) if e.type == WorkflowEventType.TASK_STARTED)
    task_completed_idx = next(i for i, e in enumerate(events) if e.type == WorkflowEventType.TASK_COMPLETED)
    
    # Verify there's a TASK_PROGRESS event between started and completed
    progress_between = [e for e in events[task_started_idx+1:task_completed_idx] 
                       if e.type == WorkflowEventType.TASK_PROGRESS]
    assert len(progress_between) == 2
    
    # Verify the final task result
    result = workflow.context.get("result")
    assert result.final_result == "Completed processing 3 items"
    assert result.execution_time > 0.01  # Should be at least delay time


@pytest.mark.asyncio
async def test_conditional_progress_events():
    """Test a task that conditionally emits progress events based on input."""
    
    async def conditional_progress_task(input: InputModel) -> AsyncIterator[Union[ProgressModel, ResultModel]]:
        """Task that conditionally emits progress events."""
        start_time = time.time()
        
        if input.should_emit_progress:
            # Emit progress events
            for i in range(input.count - 1):  # Leave room for final result
                percentage = (i + 1) / input.count * 100
                # Explicitly create progress model instances
                progress = ProgressModel(iteration=i+1, percentage=percentage)
                yield progress
                await asyncio.sleep(input.delay)
        else:
            # Just wait the total time without emitting progress
            await asyncio.sleep(input.delay * input.count)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Return final result as explicit ResultModel
        final_result = ResultModel(
            final_result=f"Completed processing {input.count} items",
            execution_time=execution_time
        )
        yield final_result
    
    # Test with progress events enabled
    workflow_with_progress = (WorkflowBuilder()
        .task("progress_enabled")
            .input_model(InputModel)
            .output_model(ResultModel)
            .progress_model(ProgressModel)
            .processor(conditional_progress_task)
            .arg("count", 3)
            .arg("should_emit_progress", True)
            .arg("delay", 0.01)
            .output("result_with_progress")
        .build()
    )
    
    # Test with progress events disabled
    workflow_without_progress = (WorkflowBuilder()
        .task("progress_disabled")
            .input_model(InputModel)
            .output_model(ResultModel)
            .progress_model(ProgressModel)
            .processor(conditional_progress_task)
            .arg("count", 3)
            .arg("should_emit_progress", False)
            .arg("delay", 0.01)
            .output("result_without_progress")
        .build()
    )
    
    # Execute both workflows and collect events
    with_progress_events = []
    async for event in workflow_with_progress.execute():
        with_progress_events.append(event)
    
    without_progress_events = []
    async for event in workflow_without_progress.execute():
        without_progress_events.append(event)
    
    # Count progress events in each case
    with_progress_count = len([e for e in with_progress_events if e.type == WorkflowEventType.TASK_PROGRESS])
    without_progress_count = len([e for e in without_progress_events if e.type == WorkflowEventType.TASK_PROGRESS])
    
    # Verify correct number of events
    assert with_progress_count == 2  # One for each iteration (except final)
    assert without_progress_count == 0  # No progress events when disabled
    
    # Verify both tasks completed
    assert workflow_with_progress.context.get("result_with_progress").final_result == "Completed processing 3 items"
    assert workflow_without_progress.context.get("result_without_progress").final_result == "Completed processing 3 items" 