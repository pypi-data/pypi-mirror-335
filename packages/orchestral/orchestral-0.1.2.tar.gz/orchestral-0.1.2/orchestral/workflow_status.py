from enum import Enum
from typing import Literal

WorkflowStatusName = Literal["COMPLETED", "FAILED", "RUNNING", "READY"]


class WorkflowStatus(Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    READY = "READY"
    RUNNING = "RUNNING"
