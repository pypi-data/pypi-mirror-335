from typing import Dict, Optional
from at_common_workflow.core.constants import TaskStatus

class Progress:
    def __init__(self):
        self.task_statuses: Dict[str, TaskStatus] = {}
        self.current_task: Optional[str] = None
        
    def update_task_status(self, task_name: str, status: TaskStatus) -> None:
        self.task_statuses[task_name] = status
        if status == TaskStatus.RUNNING:
            self.current_task = task_name
        elif self.current_task == task_name:
            self.current_task = None