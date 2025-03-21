import inspect
from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    Literal,
    TypeVar,
)

from .step_type import StepType

T = TypeVar("T")

WorkflowTask = Callable[..., Awaitable[T]] | Callable[..., T]
WorkflowStep = str | WorkflowTask[T]


class Step(Generic[T]):
    def __init__(
        self,
        step: WorkflowStep[T],
        *dependencies: list[WorkflowStep[T]],
        shell_args: tuple[str, ...],
        env: dict[str, Any] | None = None,
        cwd: str | None = None,
        shell: bool = False,
        alias: str | None = None,
        timeout: str | int | float | None = None,
        schedule: str | None = None,
        trigger: Literal["MANUAL", "ON_START"] = "MANUAL",
        repeat: int | Literal["NEVER", "ALWAYS"] = "NEVER",
        keep: int | None = None,
        max_age: str | None = None,
        keep_policy: Literal["COUNT", "AGE", "COUNT_AND_AGE"] = "COUNT",
    ):
        self.call = step
        self.dependencies = [
            dependency
            if isinstance(
                dependency,
                str,
            )
            else dependency.__name__
            for dependency in dependencies
        ]

        self.alias = alias
        self.timeout = timeout
        self.schedule = schedule
        self.trigger = trigger
        self.repeat = repeat
        self.keep = keep
        self.max_age = max_age
        self.keep_policy = keep_policy

        self.env = env
        self.cwd = cwd
        self.shell = shell
        self.shell_args = shell_args

        if isinstance(step, str):
            self.type = StepType.SHELL

        elif (
            inspect.iscoroutine(step)
            or inspect.iscoroutinefunction(step)
            or inspect.isawaitable(step)
        ):
            self.type = StepType.ASYNC

        else:
            self.type = StepType.SYNC
