# At Common Workflow

## Description
At Common Workflow is a workflow management system that allows users to define and execute tasks in a directed acyclic graph (DAG) structure. It supports parallel execution and provides a context manager for managing task inputs and outputs.

## Installation
To set up the project, follow these steps:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd at-common-workflow
   ```
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
There are two ways to define tasks: using class inheritance or using the builder pattern.

### Class-based Approach
```python
from at_common_workflow.core.task.processing_task import ProcessingTask
from pydantic import BaseModel

class AddInputModel(BaseModel):
    a: int
    b: int

class AddOutputModel(BaseModel):
    result: int

class AddTask(ProcessingTask[AddInputModel, AddOutputModel]):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            input_model=AddInputModel,
            output_model=AddOutputModel,
            processor_function=self._execute
        )
    
    async def _execute(self, input: AddInputModel) -> AddOutputModel:
        return AddOutputModel(result=input.a + input.b)

# Run workflow
from at_common_workflow.core.workflow.base import Workflow

workflow = Workflow()
task = AddTask("add_numbers")
workflow.add_task(task, argument_mappings={"a": 5, "b": 3}, result_mapping="result")
async for event in workflow.execute():
    pass
print(workflow.context.get("result").result)  # Output: 8
```

### Builder Pattern Approach (Recommended)
```python
from at_common_workflow.core.workflow.builder import WorkflowBuilder
from pydantic import BaseModel

class AddInputModel(BaseModel):
    a: int
    b: int

class AddOutputModel(BaseModel):
    result: int

async def execute_add(input: AddInputModel) -> AddOutputModel:
    return AddOutputModel(result=input.a + input.b)

# Create and execute workflow
workflow = (WorkflowBuilder()
    .task("add_numbers")
        .input_model(AddInputModel)
        .output_model(AddOutputModel)
        .processor(execute_add)
        .arg("a", 5)
        .arg("b", 3)
        .output("result")
    .build())

async for event in workflow.execute():
    pass
print(workflow.context.get("result").result)  # Output: 8
```