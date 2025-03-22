import pytest
from at_common_workflow.core.workflow import WorkflowBuilder
from at_common_workflow.core.context import Context
from at_common_workflow.core.constants import WorkflowEventType
from pydantic import BaseModel
import asyncio
import time
from typing import AsyncIterator, List, Dict, Any, Optional
import random
from at_common_workflow.core.exceptions import TaskConfigurationError
from at_common_workflow.core.exceptions import WorkflowValidationError
from at_common_workflow.core.workflow import Workflow
from at_common_workflow.core.task.processing_task import ProcessingTask
from at_common_workflow.utils.mappings import ArgumentMapping, ResultMapping

class AddInputModel(BaseModel):
    a: int
    b: int

class AddOutputModel(BaseModel):
    result: int

async def execute_add(input: AddInputModel) -> AsyncIterator[AddOutputModel]:
    yield AddOutputModel(result=input.a + input.b)

@pytest.mark.asyncio
async def test_task_builder_initialization():
    workflow = (WorkflowBuilder()
        .task("add_task")
            .input_model(AddInputModel)
            .output_model(AddOutputModel)
            .processor(execute_add)
            .arg("a", 5)
            .arg("b", 3)
            .output("add_task_result", "result")
        .build()
    )

    # Assert that the workflow is not None
    assert workflow is not None

    # Assert that the task was added to the workflow
    assert len(workflow.nodes) == 1  # Assuming only one task is added

    # Assert that the task's name is correct
    task_node = workflow.nodes[0]
    assert task_node.task.name == "add_task"

    # Assert that the input model is set correctly
    assert task_node.task.input_model is AddInputModel

    # Assert that the output model is set correctly
    assert task_node.task.output_model is AddOutputModel

    # Assert that the constant arguments are mapped correctly
    assert task_node.argument_mappings["a"].value == 5
    assert task_node.argument_mappings["b"].value == 3

    # Assert that the result mapping is set correctly
    assert task_node.result_mapping.context_key == "add_task_result"

@pytest.mark.asyncio
async def test_task_builder_with_description():
    workflow = (WorkflowBuilder()
        .task("add_task")
            .description("Adds two numbers")
            .input_model(AddInputModel)
            .output_model(AddOutputModel)
            .processor(execute_add)
            .arg("a", 5)
            .arg("b", 3)
            .output("result")
        .build()
    )
    
    assert workflow.nodes[0].task.description == "Adds two numbers"

@pytest.mark.asyncio
async def test_task_builder_with_context_arg():
    workflow = (WorkflowBuilder()
        .task("first_task")
            .input_model(AddInputModel)
            .output_model(AddOutputModel)
            .processor(execute_add)
            .arg("a", 5)
            .arg("b", 3)
            .output("first_result", "result")
        .task("second_task")
            .input_model(AddInputModel)
            .output_model(AddOutputModel)
            .processor(execute_add)
            .arg("a", from_ctx="first_result")
            .arg("b", 2)
            .output("final_result", "result")
        .build()
    )
    
    assert len(workflow.nodes) == 2
    second_task = workflow.nodes[1]
    assert second_task.argument_mappings["a"].value == "$first_result"
    assert second_task.argument_mappings["b"].value == 2

@pytest.mark.asyncio
async def test_task_builder_invalid_input_model():
    class InvalidModel:  # Not a Pydantic model
        pass
    
    with pytest.raises(TypeError, match="input_model must be a Pydantic BaseModel class"):
        (WorkflowBuilder()
            .task("invalid_task")
                .input_model(InvalidModel)
        )

@pytest.mark.asyncio
async def test_task_builder_missing_required_components():
    # Missing input model
    with pytest.raises(TaskConfigurationError):
        (WorkflowBuilder()
            .task("incomplete_task")
                .output_model(AddOutputModel)
                .processor(execute_add)
                .arg("a", 1)
                .arg("b", 2)
                .output("result")
        )
    
    # Missing output model
    with pytest.raises(TaskConfigurationError):
        (WorkflowBuilder()
            .task("incomplete_task")
                .input_model(AddInputModel)
                .processor(execute_add)
                .arg("a", 1)
                .arg("b", 2)
                .output("result")
        )
    
    # Missing processor function
    with pytest.raises(TaskConfigurationError):
        (WorkflowBuilder()
            .task("incomplete_task")
                .input_model(AddInputModel)
                .output_model(AddOutputModel)
                .arg("a", 1)
                .arg("b", 2)
                .output("result")
        )

@pytest.mark.asyncio
async def test_task_builder_invalid_constant_arg():
    # Test that values that look like context refs but aren't
    # marked as such raise errors
    with pytest.raises(TaskConfigurationError):
        (WorkflowBuilder()
            .task("invalid_arg_task")
                .input_model(AddInputModel)
                .output_model(AddOutputModel)
                .processor(execute_add)
                .arg("a", "$looks.like.context.ref")  # Should be marked as from_ctx
                .arg("b", 2)
                .output("result")
        )

@pytest.mark.asyncio
async def test_multiple_tasks_workflow():
    # Create a more complex workflow with multiple tasks
    workflow = (WorkflowBuilder()
        .task("task1")
            .input_model(AddInputModel)
            .output_model(AddOutputModel)
            .processor(execute_add)
            .arg("a", 5)
            .arg("b", 3)
            .output("result1", "result")
        .task("task2")
            .input_model(AddInputModel)
            .output_model(AddOutputModel)
            .processor(execute_add)
            .arg("a", from_ctx="result1")
            .arg("b", 2)
            .output("final_result", "result")
        .build()
    )
    
    assert len(workflow.nodes) == 2
    
    # Verify first task
    task1 = workflow.nodes[0]
    assert task1.task.name == "task1"
    assert task1.argument_mappings["a"].value == 5
    assert task1.argument_mappings["b"].value == 3
    assert task1.result_mapping.context_key == "result1"
    assert task1.result_mapping.result_path == "result"
    
    # Verify second task
    task2 = workflow.nodes[1]
    assert task2.task.name == "task2"
    assert task2.argument_mappings["a"].value == "$result1"
    assert task2.argument_mappings["b"].value == 2
    assert task2.result_mapping.context_key == "final_result"
    assert task2.result_mapping.result_path == "result"

@pytest.mark.asyncio
async def test_task_builder_invalid_output_model():
    class InvalidModel:  # Not a Pydantic model
        pass
    
    with pytest.raises(TypeError, match="output_model must be a Pydantic BaseModel class"):
        (WorkflowBuilder()
            .task("invalid_task")
                .input_model(AddInputModel)
                .output_model(InvalidModel)
        )

@pytest.mark.asyncio
async def test_task_builder_chaining():
    # Test that all builder methods return self for proper chaining
    builder = WorkflowBuilder().task("chain_task")
    
    # Test each method returns the builder instance
    assert builder.description("test") is builder
    assert builder.input_model(AddInputModel) is builder
    assert builder.output_model(AddOutputModel) is builder
    assert builder.processor(execute_add) is builder
    assert builder.arg("a", 1) is builder
    assert builder.arg("b", from_ctx="some_key") is builder

@pytest.mark.asyncio
async def test_task_builder_result_paths():
    # Create a more complex output model for testing result paths
    class ComplexOutputModel(BaseModel):
        value: int
        nested: dict
        items: list

    async def complex_execute(input: AddInputModel) -> AsyncIterator[ComplexOutputModel]:
        yield ComplexOutputModel(
            value=input.a + input.b,
            nested={"result": input.a * input.b},
            items=[input.a, input.b]
        )

    workflow = (WorkflowBuilder()
        .task("complex_task")
            .input_model(AddInputModel)
            .output_model(ComplexOutputModel)
            .processor(complex_execute)
            .arg("a", 5)
            .arg("b", 3)
            .output("result1", "value")  # Store just the value field
        .task("nested_task")
            .input_model(AddInputModel)
            .output_model(ComplexOutputModel)
            .processor(complex_execute)
            .arg("a", 2)
            .arg("b", 4)
            .output("result2", "nested.result")  # Store nested field
        .build()
    )
    
    assert len(workflow.nodes) == 2
    assert workflow.nodes[0].result_mapping.result_path == "value"
    assert workflow.nodes[1].result_mapping.result_path == "nested.result"

@pytest.mark.asyncio
async def test_task_builder_duplicate_task_names():
    workflow_builder = WorkflowBuilder()
    
    # Add first task
    workflow_builder.task("same_name") \
        .input_model(AddInputModel) \
        .output_model(AddOutputModel) \
        .processor(execute_add) \
        .arg("a", 1) \
        .arg("b", 2) \
        .output("result1")
    
    # Add second task with same name - should not raise an error as we're allowing duplicates
    # but the internal IDs should be different
    workflow_builder.task("same_name") \
        .input_model(AddInputModel) \
        .output_model(AddOutputModel) \
        .processor(execute_add) \
        .arg("a", 3) \
        .arg("b", 4) \
        .output("result2")
    
    workflow = workflow_builder.build()
    
    assert len(workflow.nodes) == 2
    assert workflow.nodes[0].task.name == "same_name"
    assert workflow.nodes[1].task.name == "same_name"
    
    # Even though names are the same, they should be different task instances
    assert workflow.nodes[0].task is not workflow.nodes[1].task

class UserInputModel(BaseModel):
    user_id: str
    user_data: dict

class UserOutputModel(BaseModel):
    processed: bool
    data: dict

async def process_user(input: UserInputModel) -> AsyncIterator[UserOutputModel]:
    yield UserOutputModel(
        processed=True,
        data={"id": input.user_id, **input.user_data}
    )

@pytest.mark.asyncio
async def test_task_builder_context_arg_variations():
    workflow = (WorkflowBuilder()
        .task("first_task")
            .input_model(UserInputModel)
            .output_model(UserOutputModel)
            .processor(process_user)
            .arg("user_id", "user123")
            .arg("user_data", {"name": "Test User", "age": 30})
            .output("user_result")
        .task("second_task")
            .input_model(UserInputModel)
            .output_model(UserOutputModel)
            .processor(process_user)
            .arg("user_id", from_ctx="user_result.data.id")  # Reference a nested path
            .arg("user_data", from_ctx="user_result.data")   # Reference the entire data field
            .output("final_result")
        .build()
    )
    
    # Verify task configurations
    assert len(workflow.nodes) == 2
    
    # Check first task
    first_task = workflow.nodes[0]
    assert first_task.argument_mappings["user_id"].value == "user123"
    assert first_task.argument_mappings["user_data"].value == {"name": "Test User", "age": 30}
    
    # Check second task
    second_task = workflow.nodes[1]
    assert second_task.argument_mappings["user_id"].value == "$user_result.data.id"
    assert second_task.argument_mappings["user_data"].value == "$user_result.data"

@pytest.mark.asyncio
async def test_task_builder_context_arg_dollar_prefix():
    workflow = (WorkflowBuilder()
        .task("first_task")
            .input_model(AddInputModel)
            .output_model(AddOutputModel)
            .processor(execute_add)
            .arg("a", 5)
            .arg("b", 3)
            .output("result1", "result")
        # Test with already dollar-prefixed reference
        .task("second_task")
            .input_model(AddInputModel)
            .output_model(AddOutputModel)
            .processor(execute_add)
            .arg("a", from_ctx="$result1")
            .arg("b", 2)
            .output("result2", "result")
        # Test with non-prefixed reference
        .task("third_task")
            .input_model(AddInputModel)
            .output_model(AddOutputModel)
            .processor(execute_add)
            .arg("a", from_ctx="result2")
            .arg("b", 3)
            .output("result3", "result")
        .build()
    )
    
    # Verify that both forms of context reference are handled correctly
    assert workflow.nodes[1].argument_mappings["a"].value == "$result1"
    assert workflow.nodes[2].argument_mappings["a"].value == "$result2"

@pytest.mark.asyncio
async def test_task_builder_context_arg_nested_paths():
    # Create a more complex output model for testing result paths
    class ComplexOutputModel(BaseModel):
        value: int
        nested: dict
        items: list

    async def complex_execute(input: AddInputModel) -> AsyncIterator[ComplexOutputModel]:
        yield ComplexOutputModel(
            value=input.a + input.b,
            nested={"result": input.a * input.b},
            items=[input.a, input.b]
        )

    workflow = (WorkflowBuilder()
        # First task produces a complex object
        .task("complex_task")
            .input_model(AddInputModel)
            .output_model(ComplexOutputModel)
            .processor(complex_execute)
            .arg("a", 5)
            .arg("b", 3)
            .output("complex_result")
        # Second task references nested paths in the complex result
        .task("nested_path_task")
            .input_model(AddInputModel)
            .output_model(AddOutputModel)
            .processor(execute_add)
            .arg("a", from_ctx="complex_result.value")  # Reference value field
            .arg("b", from_ctx="complex_result.nested.result")  # Reference nested result field
            .output("nested_result", "result")
        # Third task references array element
        .task("array_ref_task")
            .input_model(AddInputModel)
            .output_model(AddOutputModel)
            .processor(execute_add)
            .arg("a", from_ctx="complex_result.items.0")  # Reference first array element
            .arg("b", from_ctx="complex_result.items.1")  # Reference second array element
            .output("array_result", "result")
        .build()
    )
    
    # Verify nested path references
    second_task = workflow.nodes[1]
    assert second_task.argument_mappings["a"].value == "$complex_result.value"
    assert second_task.argument_mappings["b"].value == "$complex_result.nested.result"
    
    # Verify array element references
    third_task = workflow.nodes[2]
    assert third_task.argument_mappings["a"].value == "$complex_result.items.0"
    assert third_task.argument_mappings["b"].value == "$complex_result.items.1"

@pytest.mark.asyncio
async def test_workflow_execution_error_handling():
    """Test that errors during task execution are properly handled."""
    
    async def failing_execute(input: AddInputModel) -> AsyncIterator[AddOutputModel]:
        yield AddOutputModel(result=input.a + input.b)  # Yield a value first
        raise ValueError("Simulated error")  # Then raise the error
    
    workflow = (WorkflowBuilder()
        .task("failing_task")
            .input_model(AddInputModel)
            .output_model(AddOutputModel)
            .processor(failing_execute)
            .arg("a", 5)
            .arg("b", 3)
            .output("result")
        .build()
    )
    
    # Execute workflow and expect an error
    with pytest.raises(RuntimeError):
        async for _ in workflow.execute():
            pass

@pytest.mark.asyncio
async def test_workflow_cyclic_dependencies():
    """Test that cyclic dependencies are detected during validation."""
    # Create a workflow with cyclic dependencies: A -> B -> A
    builder = WorkflowBuilder()
    
    # First task depends on the second task's output
    builder.task("taskA") \
        .input_model(AddInputModel) \
        .output_model(AddOutputModel) \
        .processor(execute_add) \
        .arg("a", from_ctx="resultB") \
        .arg("b", 2) \
        .output("resultA")
    
    # Second task depends on the first task's output
    builder.task("taskB") \
        .input_model(AddInputModel) \
        .output_model(AddOutputModel) \
        .processor(execute_add) \
        .arg("a", from_ctx="resultA") \
        .arg("b", 3) \
        .output("resultB")
        
    # This should raise WorkflowValidationError due to the cycle
    with pytest.raises(WorkflowValidationError):
        builder.build()

@pytest.mark.asyncio
async def test_workflow_events():
    """Test that workflow events are emitted correctly."""
    
    workflow = (WorkflowBuilder()
        .task("add_task")
            .input_model(AddInputModel)
            .output_model(AddOutputModel)
            .processor(execute_add)
            .arg("a", 5)
            .arg("b", 3)
            .output("result")
        .build()
    )
    
    events = []
    async for event in workflow.execute():
        events.append(event)
    
    # Verify events
    assert len(events) >= 3  # At least WORKFLOW_STARTED, TASK_STARTED, TASK_COMPLETED, WORKFLOW_COMPLETED
    assert events[0].type == WorkflowEventType.WORKFLOW_STARTED
    assert any(e.type == WorkflowEventType.TASK_STARTED and e.task_name == "add_task" for e in events)
    assert any(e.type == WorkflowEventType.TASK_COMPLETED and e.task_name == "add_task" for e in events)
    assert events[-1].type == WorkflowEventType.WORKFLOW_COMPLETED

@pytest.mark.asyncio
async def test_parallel_task_execution():
    """Test that independent tasks execute in parallel."""
    
    # Create a task that takes some time to complete
    async def slow_execute(input: AddInputModel) -> AsyncIterator[AddOutputModel]:
        await asyncio.sleep(0.1)  # Simulate work
        yield AddOutputModel(result=input.a + input.b)
    
    # Create a workflow with two independent tasks
    workflow = (WorkflowBuilder()
        .task("task1")
            .input_model(AddInputModel)
            .output_model(AddOutputModel)
            .processor(slow_execute)
            .arg("a", 1)
            .arg("b", 2)
            .output("result1")
        .task("task2")
            .input_model(AddInputModel)
            .output_model(AddOutputModel)
            .processor(slow_execute)
            .arg("a", 3)
            .arg("b", 4)
            .output("result2")
        .build()
    )
    
    # Execute and time it
    start_time = time.time()
    async for _ in workflow.execute():
        pass
    execution_time = time.time() - start_time
    
    # If tasks ran in parallel, execution time should be close to 0.1s
    # If they ran sequentially, it would be closer to 0.2s
    assert execution_time < 0.15  # Allow some margin for test overhead

class StreamingInputModel(BaseModel):
    count: int

class StreamingOutputModel(BaseModel):
    value: int

async def streaming_counter(input: StreamingInputModel) -> AsyncIterator[StreamingOutputModel]:
    """Example streaming task that yields numbers up to count."""
    for i in range(input.count):
        yield StreamingOutputModel(value=i)
        await asyncio.sleep(0.1)  # Simulate some processing time

@pytest.mark.asyncio
async def test_streaming_task():
    """Test that streaming tasks emit events correctly."""
    
    workflow = (WorkflowBuilder()
        .task("counter")
            .input_model(StreamingInputModel)
            .output_model(StreamingOutputModel)
            .processor(streaming_counter)
            .arg("count", 5)
            .output("final_count")
        .build()
    )
    
    events = []
    async for event in workflow.execute():
        events.append(event)
    
    # Verify events
    assert len(events) >= 7  # WORKFLOW_STARTED + TASK_STARTED + 5 TASK_PROGRESS + TASK_COMPLETED + WORKFLOW_COMPLETED
    assert events[0].type == WorkflowEventType.WORKFLOW_STARTED
    
    # Verify streaming events
    stream_events = [e for e in events if e.type == WorkflowEventType.TASK_PROGRESS]
    assert len(stream_events) == 5
    
    # Verify stream data values
    for i, event in enumerate(stream_events):
        assert event.task_name == "counter"
        assert event.task_data.value == i
    
    assert events[-1].type == WorkflowEventType.WORKFLOW_COMPLETED

@pytest.mark.asyncio
async def test_realtime_event_reporting():
    """Test that events are reported in real-time rather than batched at the end."""
    
    # Create a task that yields values with delays between them
    async def delayed_counter(input: StreamingInputModel) -> AsyncIterator[StreamingOutputModel]:
        for i in range(input.count):
            yield StreamingOutputModel(value=i)
            await asyncio.sleep(0.2)  # Significant delay between events
    
    workflow = (WorkflowBuilder()
        .task("delayed_counter")
            .input_model(StreamingInputModel)
            .output_model(StreamingOutputModel)
            .processor(delayed_counter)
            .arg("count", 3)
            .output("final_count")
        .build()
    )
    
    # Collect events with timestamps
    events_with_time = []
    start_time = time.time()
    
    async for event in workflow.execute():
        event_time = time.time() - start_time
        events_with_time.append((event, event_time))
    
    # Extract just the progress events with their timestamps
    progress_events = [(e, t) for e, t in events_with_time 
                      if e.type == WorkflowEventType.TASK_PROGRESS]
    
    # Verify we got the expected number of progress events
    assert len(progress_events) == 3
    
    # Check that events were received with appropriate timing
    # If events were batched at the end, all timestamps would be very close together
    # With real-time reporting, they should be spaced out by approximately the sleep time
    
    # First event should come relatively quickly
    assert progress_events[0][1] < 0.3  # Allow some overhead
    
    # Subsequent events should be spaced by approximately the sleep time
    for i in range(1, len(progress_events)):
        time_diff = progress_events[i][1] - progress_events[i-1][1]
        assert 0.15 < time_diff < 0.3  # Should be close to the 0.2s sleep time
    
    # The last progress event should be well before the end of execution
    # This verifies events weren't all held until the end
    last_event_time = events_with_time[-1][1]
    last_progress_time = progress_events[-1][1]
    assert last_event_time - last_progress_time > 0.1

@pytest.mark.asyncio
async def test_concurrent_streaming_tasks():
    """Test that multiple streaming tasks can report events in real-time concurrently."""
    
    # Create tasks with different speeds
    async def fast_counter(input: StreamingInputModel) -> AsyncIterator[StreamingOutputModel]:
        for i in range(input.count):
            yield StreamingOutputModel(value=i)
            await asyncio.sleep(0.1)  # Fast task
    
    async def slow_counter(input: StreamingInputModel) -> AsyncIterator[StreamingOutputModel]:
        for i in range(input.count):
            yield StreamingOutputModel(value=i * 10)
            await asyncio.sleep(0.2)  # Slow task
    
    # Build workflow with two independent streaming tasks
    workflow = (WorkflowBuilder()
        .task("fast_task")
            .input_model(StreamingInputModel)
            .output_model(StreamingOutputModel)
            .processor(fast_counter)
            .arg("count", 5)
            .output("fast_result")
        .task("slow_task")
            .input_model(StreamingInputModel)
            .output_model(StreamingOutputModel)
            .processor(slow_counter)
            .arg("count", 3)
            .output("slow_result")
        .build()
    )
    
    # Collect events with timestamps and task names
    events = []
    start_time = time.time()
    
    async for event in workflow.execute():
        event_time = time.time() - start_time
        events.append((event, event_time))
    
    # Extract progress events by task
    fast_events = [(e, t) for e, t in events 
                  if e.type == WorkflowEventType.TASK_PROGRESS and e.task_name == "fast_task"]
    slow_events = [(e, t) for e, t in events 
                  if e.type == WorkflowEventType.TASK_PROGRESS and e.task_name == "slow_task"]
    
    # Verify we got the expected number of events
    assert len(fast_events) == 5
    assert len(slow_events) == 3
    
    # Verify the events are interleaved - we should see events from both tasks
    # before either task completes
    
    # Get the time of the last event from each task
    last_fast_time = fast_events[-1][1]
    last_slow_time = slow_events[-1][1]
    
    # Get all events that occurred before both tasks completed
    early_events = [e for e, t in events if t < min(last_fast_time, last_slow_time)]
    
    # We should see progress events from both tasks in the early events
    fast_progress_in_early = any(e.type == WorkflowEventType.TASK_PROGRESS and e.task_name == "fast_task" 
                               for e in early_events)
    slow_progress_in_early = any(e.type == WorkflowEventType.TASK_PROGRESS and e.task_name == "slow_task" 
                               for e in early_events)
    
    assert fast_progress_in_early, "Should see progress events from fast task before both tasks complete"
    assert slow_progress_in_early, "Should see progress events from slow task before both tasks complete"
    
    # Verify that the fast task completes before the slow task
    # (since it has more iterations but runs twice as fast)
    fast_completed_event = next((e, t) for e, t in events 
                              if e.type == WorkflowEventType.TASK_COMPLETED and e.task_name == "fast_task")
    slow_completed_event = next((e, t) for e, t in events 
                              if e.type == WorkflowEventType.TASK_COMPLETED and e.task_name == "slow_task")
    
    # The fast task should complete in about 0.5s, the slow task in about 0.6s
    assert fast_completed_event[1] < slow_completed_event[1]

@pytest.mark.asyncio
async def test_streaming_task_error_handling():
    """Test that errors in streaming tasks are properly handled and reported."""
    
    async def streaming_with_error(input: StreamingInputModel) -> AsyncIterator[StreamingOutputModel]:
        # Yield a few values successfully
        for i in range(2):
            yield StreamingOutputModel(value=i)
            await asyncio.sleep(0.1)
        
        # Then raise an error
        raise ValueError("Simulated error in streaming task")
    
    workflow = (WorkflowBuilder()
        .task("error_stream")
            .input_model(StreamingInputModel)
            .output_model(StreamingOutputModel)
            .processor(streaming_with_error)
            .arg("count", 5)  # We'll only get to 2 before error
            .output("result")
        .build()
    )
    
    # Collect events until error
    events = []
    with pytest.raises(RuntimeError) as excinfo:
        async for event in workflow.execute():
            events.append(event)
    
    # Verify error message
    assert "task failure" in str(excinfo.value)
    
    # Verify we got the expected events before the error
    assert events[0].type == WorkflowEventType.WORKFLOW_STARTED
    assert any(e.type == WorkflowEventType.TASK_STARTED and e.task_name == "error_stream" for e in events)
    
    # We should have received 2 progress events before the error
    progress_events = [e for e in events if e.type == WorkflowEventType.TASK_PROGRESS]
    assert len(progress_events) == 2
    
    # Verify the progress event values
    assert progress_events[0].task_data.value == 0
    assert progress_events[1].task_data.value == 1
    
    # We should have a task failed event
    failed_events = [e for e in events if e.type == WorkflowEventType.TASK_FAILED]
    assert len(failed_events) == 1
    
    # The error should be a ModelValidationError wrapping the original ValueError
    from at_common_workflow.core.exceptions import ModelValidationError
    assert isinstance(failed_events[0].error, ModelValidationError)
    assert "Simulated error in streaming task" in str(failed_events[0].error)

class SlowTaskInputModel(BaseModel):
    delay: float
    task_id: str

class SlowTaskOutputModel(BaseModel):
    result: str
    execution_time: float
    task_id: str

class CombineInputModel(BaseModel):
    fast: str
    medium: str
    slow: str
    fast_time: float
    medium_time: float
    slow_time: float

class CombineOutputModel(BaseModel):
    combined: str
    timing_info: dict

async def execute_slow_task(input: SlowTaskInputModel) -> AsyncIterator[SlowTaskOutputModel]:
    """Task that executes with the specified delay."""
    start_time = time.time()
    
    # Simulate work
    await asyncio.sleep(input.delay)
    
    # Calculate total execution time
    execution_time = time.time() - start_time
    
    # Return result
    yield SlowTaskOutputModel(
        result=f"Task {input.task_id} completed",
        execution_time=execution_time,
        task_id=input.task_id
    )

async def execute_combine(input: CombineInputModel) -> AsyncIterator[CombineOutputModel]:
    """Task that combines results from other tasks."""
    # Create a combined result
    combined = f"{input.fast}, {input.medium}, {input.slow}"
    
    # Create timing info
    timing_info = {
        "fast": input.fast_time,
        "medium": input.medium_time,
        "slow": input.slow_time
    }
    
    # Return the combined result
    yield CombineOutputModel(
        combined=combined,
        timing_info=timing_info
    )

@pytest.mark.asyncio
async def test_tasks_with_different_speeds():
    """Test a workflow with tasks that execute at different speeds."""
    builder = WorkflowBuilder()
    
    # Fast task (no delay)
    (builder.task("fast_task")
        .input_model(SlowTaskInputModel)
        .output_model(SlowTaskOutputModel)
        .processor(execute_slow_task)
        .arg("delay", 0.01)
        .arg("task_id", "fast")
        .output("fast_result", "result"))
    
    # Add another task that extracts the execution time from the same result
    (builder.task("fast_time_task")
        .input_model(SlowTaskInputModel)
        .output_model(SlowTaskOutputModel)
        .processor(execute_slow_task)
        .arg("delay", 0.01)
        .arg("task_id", "fast")
        .output("fast_time", "execution_time"))
    
    # Medium task
    (builder.task("medium_task")
        .input_model(SlowTaskInputModel)
        .output_model(SlowTaskOutputModel)
        .processor(execute_slow_task)
        .arg("delay", 0.1)
        .arg("task_id", "medium")
        .output("medium_result", "result"))
    
    # Add another task that extracts the execution time from the same result
    (builder.task("medium_time_task")
        .input_model(SlowTaskInputModel)
        .output_model(SlowTaskOutputModel)
        .processor(execute_slow_task)
        .arg("delay", 0.1)
        .arg("task_id", "medium")
        .output("medium_time", "execution_time"))
    
    # Slow task
    (builder.task("slow_task")
        .input_model(SlowTaskInputModel)
        .output_model(SlowTaskOutputModel)
        .processor(execute_slow_task)
        .arg("delay", 0.5)
        .arg("task_id", "slow")
        .output("slow_result", "result"))
    
    # Add another task that extracts the execution time from the same result
    (builder.task("slow_time_task")
        .input_model(SlowTaskInputModel)
        .output_model(SlowTaskOutputModel)
        .processor(execute_slow_task)
        .arg("delay", 0.5)
        .arg("task_id", "slow")
        .output("slow_time", "execution_time"))
    
    # Combine all results
    (builder.task("combine_task")
        .input_model(CombineInputModel)
        .output_model(CombineOutputModel)
        .processor(execute_combine)
        .arg("fast", from_ctx="fast_result")
        .arg("medium", from_ctx="medium_result")
        .arg("slow", from_ctx="slow_result")
        .arg("fast_time", from_ctx="fast_time")
        .arg("medium_time", from_ctx="medium_time")
        .arg("slow_time", from_ctx="slow_time")
        .output("combined_result"))

    workflow = builder.build()
    
    # Execute the workflow
    events = []
    
    async for event in workflow.execute():
        events.append(event)
    
    # Verify all tasks completed
    assert "fast_result" in workflow.context
    assert "medium_result" in workflow.context
    assert "slow_result" in workflow.context
    
    # Verify execution times
    assert workflow.context.get("fast_time") < workflow.context.get("medium_time")
    assert workflow.context.get("medium_time") < workflow.context.get("slow_time")
    
    # Check event order - tasks should complete in order of speed
    task_completion_order = []
    for event in events:
        if event.type == WorkflowEventType.TASK_COMPLETED:
            task_completion_order.append(event.task_name)
    
    # Fast should complete before medium, medium before slow
    fast_idx = task_completion_order.index("fast_task")
    medium_idx = task_completion_order.index("medium_task")
    slow_idx = task_completion_order.index("slow_task")
    
    assert fast_idx < medium_idx < slow_idx

class CancellableTaskInputModel(BaseModel):
    task_id: str
    iterations: int
    delay_per_iteration: float

class CancellableTaskOutputModel(BaseModel):
    task_id: str
    iteration: int
    is_complete: bool

async def execute_cancellable_task(input: CancellableTaskInputModel) -> AsyncIterator[CancellableTaskOutputModel]:
    for i in range(input.iterations):
        # Check if cancelled between iterations
        if asyncio.current_task().cancelled():
            yield CancellableTaskOutputModel(
                task_id=input.task_id,
                iteration=i,
                is_complete=False
            )
            return
            
        # Sleep a bit to simulate work
        await asyncio.sleep(input.delay_per_iteration)
        
        # Yield progress
        yield CancellableTaskOutputModel(
            task_id=input.task_id,
            iteration=i + 1,
            is_complete=(i + 1 == input.iterations)
        )

@pytest.mark.asyncio
async def test_workflow_cancellation():
    """Test cancelling a workflow during execution."""
    builder = WorkflowBuilder()
    
    builder = (builder
        .task("long_running_task")
            .input_model(CancellableTaskInputModel)
            .output_model(CancellableTaskOutputModel)
            .processor(execute_cancellable_task)
            .arg("task_id", "long_task")
            .arg("iterations", 10)
            .arg("delay_per_iteration", 0.1)
            .output("task_result", "is_complete")
    )
    
    workflow = builder.build()
    
    # Execute the workflow in a separate task so we can cancel it
    events = []
    
    # Create a task for the workflow execution
    execution_task = asyncio.create_task(
        collect_events(workflow, events)
    )
    
    # Wait a bit to let it start
    await asyncio.sleep(0.3)
    
    # Cancel the task
    execution_task.cancel()
    
    try:
        await execution_task
    except asyncio.CancelledError:
        pass
    
    # Check that we got some events but not all
    assert len(events) > 0
    assert len(events) < 10  # Should be fewer than the total iterations
    
    # Since we can't check for WORKFLOW_CANCELLED (it doesn't exist in the enum),
    # we'll just verify that we got some events but not all the expected ones
    task_started = False
    for event in events:
        if hasattr(event, 'task_name') and event.task_name == "long_running_task":
            task_started = True
            break
    
    assert task_started, "Task should have started before cancellation"
    
    # Clean up any pending tasks
    for task in asyncio.all_tasks():
        if task is not asyncio.current_task() and not task.done():
            task.cancel()
            try:
                # Give it a moment to clean up
                await asyncio.wait_for(task, timeout=0.1)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass

async def collect_events(workflow, events_list):
    """Helper function to collect events from a workflow execution."""
    try:
        async for event in workflow.execute():
            events_list.append(event)
    except asyncio.CancelledError:
        # Handle cancellation gracefully
        pass
        
    return events_list

class TimeoutTaskInputModel(BaseModel):
    delay: float

class TimeoutTaskOutputModel(BaseModel):
    result: str

@pytest.mark.asyncio
async def test_task_timeout():
    """Test handling task timeouts."""
    # Create a workflow with a task that will timeout
    builder = WorkflowBuilder()
    
    # Since with_timeout is not available, we'll simulate a timeout by using a custom task
    # that checks the elapsed time and raises a TimeoutError if it exceeds the limit
    
    async def timeout_aware_task(input: TimeoutTaskInputModel) -> AsyncIterator[TimeoutTaskOutputModel]:
        start_time = time.time()
        timeout_limit = 0.1  # 100ms timeout
        
        # Sleep for the requested delay
        await asyncio.sleep(min(input.delay, 0.01))  # Small sleep to allow for task to start
        
        # Check if we've exceeded the timeout
        elapsed = time.time() - start_time
        if elapsed + input.delay > timeout_limit:
            # Simulate a timeout by raising a TimeoutError
            raise asyncio.TimeoutError(f"Task timed out after {elapsed:.2f}s")
            
        # Complete the full delay
        await asyncio.sleep(input.delay - 0.01)
        yield TimeoutTaskOutputModel(result="Completed")
    
    builder = (builder
        .task("timeout_task")
            .input_model(TimeoutTaskInputModel)
            .output_model(TimeoutTaskOutputModel)
            .processor(timeout_aware_task)
            .arg("delay", 0.5)  # Task takes 0.5 seconds, but will timeout at 0.1
            .output("timeout_result", "result")
    )
    
    workflow = builder.build()
    
    # Execute the workflow
    events = []
    
    # We expect a RuntimeError due to the TimeoutError in the task
    with pytest.raises(RuntimeError) as excinfo:
        async for event in workflow.execute():
            events.append(event)
    
    # Verify the error message contains the task name
    assert "timeout_task" in str(excinfo.value)
    
    # Result should not be in context
    assert "timeout_result" not in workflow.context

@pytest.mark.asyncio
async def test_large_workflow():
    """Test a workflow with many tasks."""
    # Create a workflow with 50 tasks
    builder = WorkflowBuilder()
    
    # Add 50 simple addition tasks
    num_tasks = 50
    for i in range(num_tasks):
        builder = (builder
            .task(f"add_task_{i}")
                .input_model(AddInputModel)
                .output_model(AddOutputModel)
                .processor(execute_add)
                .arg("a", i)
                .arg("b", i + 1)
                .output(f"result_{i}", "result")
        )
    
    workflow = builder.build()
    
    # Verify workflow structure
    assert len(workflow.nodes) == num_tasks
    
    # Execute the workflow
    events = []
    
    async for event in workflow.execute():
        events.append(event)
    
    # Verify all tasks completed
    assert len(events) > num_tasks  # Should have at least one event per task
    
    # Verify all results are stored in context
    for i in range(num_tasks):
        assert workflow.context.get(f"result_{i}") == 2 * i + 1  # a + b = i + (i + 1)

@pytest.mark.asyncio
async def test_workflow_with_nested_paths():
    """Test a workflow with nested path arguments."""
    workflow = (
        WorkflowBuilder()
        .task("extract_from_data")
            .input_model(ExtractInputModel)
            .output_model(ExtractOutputModel)
            .processor(extract_value)
            .arg("data", from_ctx="user_data")
            .arg("path", "profile.settings.theme")
            .output("theme")
        .build()
    )
    
    # Create context with nested data
    user_data = {
        "profile": {
            "name": "Test User",
            "settings": {
                "theme": "dark",
                "notifications": True
            }
        }
    }
    
    initial_context = Context({"user_data": user_data})
    
    # Execute the workflow
    try:
        async for _ in workflow.execute(initial_context):
            pass
        
        # Verify results
        assert workflow.context.get("theme").value == "dark"
    except Exception as e:
        pytest.fail(f"Workflow execution failed: {str(e)}")


class ExtractInputModel(BaseModel):
    data: Dict[str, Any]
    path: str
    
class ExtractOutputModel(BaseModel):
    value: Any


async def extract_value(input: ExtractInputModel) -> ExtractOutputModel:
    """Extract a value from a nested dictionary using a dot path."""
    parts = input.path.split('.')
    current = input.data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise ValueError(f"Path '{input.path}' is invalid")
    return ExtractOutputModel(value=current)

@pytest.mark.asyncio
async def test_task_builder_nested_output_keys():
    """Test that TaskBuilder's output function supports nested context keys."""
    # Create models for testing
    class AddInputModel(BaseModel):
        a: int
        b: int
        
    class AddOutputModel(BaseModel):
        result: int
        
    # Create an execution function
    async def execute_add(input: AddInputModel) -> AsyncIterator[AddOutputModel]:
        yield AddOutputModel(result=input.a + input.b)
        
    # Build a workflow with nested output keys
    workflow = (WorkflowBuilder()
        .task("add_task1")
            .input_model(AddInputModel)
            .output_model(AddOutputModel)
            .processor(execute_add)
            .arg("a", 5)
            .arg("b", 3)
            .output("math.operations.addition")  # Nested context key
        .task("add_task2")
            .input_model(AddInputModel)
            .output_model(AddOutputModel)
            .processor(execute_add)
            .arg("a", from_ctx="math.operations.addition.result")  # Reference nested result
            .arg("b", 2)
            .output("math.operations.second_addition.value", "result")  # Nested key with result path
        .build()
    )
    
    # Verify the nested context keys in the result mappings
    assert workflow.nodes[0].result_mapping.context_key == "math.operations.addition"
    assert workflow.nodes[1].result_mapping.context_key == "math.operations.second_addition.value"
    
    # Run the workflow and check results
    async for _ in workflow.execute():
        pass  # Just wait for the workflow to complete
    
    # Print the context structure for debugging
    print("Context data structure:", workflow.context.to_dict())
    
    # Getting the Pydantic model from the context
    addition_result = workflow.context.get("math.operations.addition")
    assert addition_result.result == 8  # Access through the model
    
    # Directly access the second addition value
    assert workflow.context.get("math.operations.second_addition.value") == 10
    
    # Verify via nested access
    math_ops = workflow.context.get("math")
    assert math_ops["operations"]["addition"].result == 8  # Access through the model
    assert math_ops["operations"]["second_addition"]["value"] == 10

@pytest.mark.asyncio
async def test_workflow_with_nested_path_in_arguments():
    """Test a workflow with nested paths like 'indicators_and_patterns.indicators' in arguments."""
    class IndicatorsInputModel(BaseModel):
        symbol: str
    
    class IndicatorsAndPatternsModel(BaseModel):
        indicators: dict
        patterns: dict
        
    class GenerateQAInputModel(BaseModel):
        profile: dict
        quote: dict
        eod: list
        indicators: dict
        patterns: dict
        news: list
        
    class GenerateQAOutputModel(BaseModel):
        qa_list: list
        
    async def mock_process_indicators(input: IndicatorsInputModel) -> AsyncIterator[IndicatorsAndPatternsModel]:
        yield IndicatorsAndPatternsModel(
            indicators={"rsi": 42, "macd": 1.5},
            patterns={"doji": True, "engulfing": False}
        )
    
    async def mock_generate_qa(input: GenerateQAInputModel) -> AsyncIterator[GenerateQAOutputModel]:
        # Verify we received the correct nested paths
        assert input.indicators == {"rsi": 42, "macd": 1.5}
        assert input.patterns == {"doji": True, "engulfing": False}
        yield GenerateQAOutputModel(qa_list=["Question 1", "Answer 1"])
    
    # Build workflow similar to the example in the issue
    workflow = (WorkflowBuilder()
        .task("get_indicators_and_patterns")
            .input_model(IndicatorsInputModel)
            .output_model(IndicatorsAndPatternsModel)
            .processor(mock_process_indicators)
            .arg("symbol", "AAPL")
            .output("indicators_and_patterns")
        .task("generate_qa")
            .input_model(GenerateQAInputModel)
            .output_model(GenerateQAOutputModel)
            .processor(mock_generate_qa)
            .arg("profile", {})  # Dummy values for testing
            .arg("quote", {})
            .arg("eod", [])
            .arg("indicators", from_ctx="indicators_and_patterns.indicators")
            .arg("patterns", from_ctx="indicators_and_patterns.patterns")
            .arg("news", [])
            .output("qa_list", result_path="qa_list")
        .build()
    )
    
    # Execute the workflow
    async for _ in workflow.execute():
        pass
    
    # Verify the workflow executed successfully
    assert "qa_list" in workflow.context.to_dict()
    assert workflow.context.get("qa_list") == ["Question 1", "Answer 1"]