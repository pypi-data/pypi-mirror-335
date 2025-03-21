import asyncio
import time
import traceback
from collections import defaultdict
from typing import Dict, List

from taskex import Env
from taskex.run import Run
from taskex.util import TimeParser
from .error import OrchestralTaskFailure
from .step_type import StepType
from .workflow import Workflow
from .workflow_status import WorkflowStatus


class Orchestral:
    def __init__(
        self,
        config: Env | None = None,
    ) -> None:
        self._workflow = Workflow(config=config)

        self._execution_orders: Dict[str, List[List[str]]] = {}
        self._batch_results: list[Run] = []
        self._results_waiter = asyncio.Event()
        self._run_task: asyncio.Task | None = None
        self._execute_next = False

        self.results: dict[str, dict[int, Run]] = defaultdict(dict)
        self.error: Exception | None = None
        self.trace: str | None = None
        self._start: float | int = 0
        self.elapsed: float = 0

    def __enter__(self):
        self._workflow = Workflow()
        return self._workflow

    def __exit__(self, type, value, traceback):
        pass

    @property
    def status(self):
        if self._workflow:
            return self._workflow.status

    async def __aiter__(self):
        # Before we yield results wait
        if self._results_waiter.is_set() is False:
            await self._results_waiter.wait()

        results = list(self._batch_results)

        yield results

    def create(self):
        self._workflow = Workflow()
        return self._workflow

    async def run(
        self,
        wait: bool = False,
        fail_fast: bool = False,
        timeout: str | int | float | None = None,
    ):
        if isinstance(timeout, str):
            timeout = TimeParser(timeout).time

        try:
            self._start = time.monotonic()

            if wait and timeout:
                await asyncio.wait_for(self._run_workflow(
                    fail_fast=fail_fast,
                ), timeout=timeout)

            elif wait:
                await self._run_workflow(
                    fail_fast=fail_fast,
                )

            elif timeout:
                self._run_task = asyncio.create_task(
                    asyncio.wait_for(
                        self._run_workflow(),
                        timeout=timeout,
                    ),
                )

            else:
                self._run_task = asyncio.create_task(
                    self._run_workflow(),
                )

        except asyncio.TimeoutError:
            self.elapsed = time.monotonic() - self._start
            self.trace = traceback.format_exc()
            self.error = Exception(
                f"Err. - Workflow exceeded timeout of {timeout} seconds"
            )

        except Exception as err:
            self.elapsed = time.monotonic() - self._start
            self.trace = traceback.format_exc()
            self.error = err

            self._workflow.status = WorkflowStatus.FAILED

    async def _run_workflow(
        self,
        fail_fast: bool = True,
    ):
        self._execute_next = True
        self._workflow.status = WorkflowStatus.READY

        for group in self._workflow:
            self._batch_results.clear()

            group_runs = [
                self._workflow.runner.command(
                    step.call,
                    *step.shell_args,
                    alias=step.alias,
                    env=step.env,
                    cwd=step.cwd,
                    shell=step.shell,
                    timeout=step.timeout,
                    schedule=step.schedule,
                    trigger=step.trigger,
                    repeat=step.repeat,
                    keep=step.keep,
                    max_age=step.max_age,
                    keep_policy=step.keep_policy,
                )
                if step.type == StepType.SHELL
                else self._workflow.runner.run(
                    step.call,
                    alias=step.alias,
                    timeout=step.timeout,
                    schedule=step.schedule,
                    trigger=step.trigger,
                    repeat=step.repeat,
                    keep=step.keep,
                    max_age=step.max_age,
                    keep_policy=step.keep_policy,
                )
                for step in group
            ]

            group_results = await self._workflow.runner.wait_all(
                [run.token for run in group_runs],
            )

            if fail_fast:
                for res in group_results:
                    if res.error:
                        return OrchestralTaskFailure(res.error, res.trace)

            self._batch_results.extend(group_results)

            for res in group_results:
                self.results[res.task_name][res.run_id] = res

            if self._results_waiter.is_set() is False:
                self._results_waiter.set()

            if self._execute_next is False:
                break

        self.elapsed = time.monotonic() - self._start
        self._workflow.status = WorkflowStatus.COMPLETED

    async def stop(self):
        self._execute_next = False
        await self._workflow.runner.stop()

    async def shutdown(self):
        self._execute_next = False
        await self._workflow.runner.shutdown()

        if self._run_task:
            await self._run_task

        if self._results_waiter.is_set() is False:
            self._results_waiter.set()

    def abort(self):
        self._execute_next = False

        try:
            self._run_task.cancel()

        except (
            asyncio.CancelledError,
            asyncio.InvalidStateError,
            asyncio.TimeoutError,
        ):
            pass

        if self._results_waiter.is_set() is False:
            self._results_waiter.set()

        self._workflow.runner.abort()
