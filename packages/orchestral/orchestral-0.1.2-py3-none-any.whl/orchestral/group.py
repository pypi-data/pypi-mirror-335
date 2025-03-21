import functools
from typing import Any, Literal, TypeVar

from .step import Step, WorkflowTask

T = TypeVar("T")


class Group:
    def __init__(
        self,
        group_id: int,
    ):
        self.id = group_id
        self._steps: list[Step[T]] = []

    def __iter__(self):
        for step in self._steps:
            yield step

    def add_task(
        self,
        step: WorkflowTask[T],
        *args: tuple[Any, ...],
        alias: str | None = None,
        timeout: str | int | float | None = None,
        schedule: str | None = None,
        trigger: Literal["MANUAL", "ON_START"] = "MANUAL",
        repeat: int | Literal["NEVER", "ALWAYS"] = "NEVER",
        keep: int | None = None,
        max_age: str | None = None,
        keep_policy: Literal["COUNT", "AGE", "COUNT_AND_AGE"] = "COUNT",
        **kwargs: dict[str, Any],
    ):
        self._steps.append(
            Step(
                functools.partial(
                    step,
                    *args,
                    **kwargs,
                ),
                alias=alias,
                timeout=timeout,
                schedule=schedule,
                trigger=trigger,
                repeat=repeat,
                keep=keep,
                max_age=max_age,
                keep_policy=keep_policy,
            )
        )

    def add_command(
        self,
        step: str,
        *args: tuple[str],
        alias: str | None = None,
        env: dict[str, Any] | None = None,
        cwd: str | None = None,
        shell: bool = False,
        timeout: str | int | float | None = None,
        schedule: str | None = None,
        trigger: Literal["MANUAL", "ON_START"] = "MANUAL",
        repeat: int | Literal["NEVER", "ALWAYS"] = "NEVER",
        keep: int | None = None,
        max_age: str | None = None,
        keep_policy: Literal["COUNT", "AGE", "COUNT_AND_AGE"] = "COUNT",
    ):
        self._steps.append(
            Step(
                step,
                shell_args=args,
                env=env,
                cwd=cwd,
                shell=shell,
                alias=alias,
                timeout=timeout,
                schedule=schedule,
                trigger=trigger,
                repeat=repeat,
                keep=keep,
                max_age=max_age,
                keep_policy=keep_policy,
            )
        )
