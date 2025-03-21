from typing import Dict, List, TypeVar

from taskex import Env, TaskRunner

from .group import Group
from .workflow_status import WorkflowStatus

T = TypeVar("T")


class Workflow:
    def __init__(
        self,
        config: Env | None = None,
    ) -> None:
        self._groups: list[Group] = []
        self._execution_orders: Dict[str, List[List[str]]] = {}
        self.runner = TaskRunner(config=config)
        self.status = WorkflowStatus.READY

    def __iter__(self):
        for group in self._groups:
            yield group

    def group(self):
        group = Group(self.runner._snowflake_generator.generate())
        self._groups.append(group)
        return group
