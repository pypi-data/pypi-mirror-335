import asyncio
import inspect
import logging
import sys
from datetime import datetime, timedelta, timezone
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    Mapping,
    Protocol,
    Self,
    TypeVar,
    cast,
)
from uuid import uuid4

import redis.exceptions
from opentelemetry import propagate, trace
from opentelemetry.trace import Tracer

from .docket import (
    Docket,
    Execution,
    RedisMessage,
    RedisMessageID,
    RedisMessages,
    RedisReadGroupResponse,
)
from .instrumentation import (
    QUEUE_DEPTH,
    REDIS_DISRUPTIONS,
    SCHEDULE_DEPTH,
    TASK_DURATION,
    TASK_PUNCTUALITY,
    TASKS_COMPLETED,
    TASKS_FAILED,
    TASKS_PERPETUATED,
    TASKS_RETRIED,
    TASKS_RUNNING,
    TASKS_STARTED,
    TASKS_STRICKEN,
    TASKS_SUCCEEDED,
    message_getter,
    metrics_server,
)

logger: logging.Logger = logging.getLogger(__name__)
tracer: Tracer = trace.get_tracer(__name__)


if TYPE_CHECKING:  # pragma: no cover
    from .dependencies import Dependency

D = TypeVar("D", bound="Dependency")


class _stream_due_tasks(Protocol):
    async def __call__(
        self, keys: list[str], args: list[str | float]
    ) -> tuple[int, int]: ...  # pragma: no cover


class Worker:
    docket: Docket
    name: str
    concurrency: int
    redelivery_timeout: timedelta
    reconnection_delay: timedelta
    minimum_check_interval: timedelta

    def __init__(
        self,
        docket: Docket,
        name: str | None = None,
        concurrency: int = 10,
        redelivery_timeout: timedelta = timedelta(minutes=5),
        reconnection_delay: timedelta = timedelta(seconds=5),
        minimum_check_interval: timedelta = timedelta(milliseconds=100),
    ) -> None:
        self.docket = docket
        self.name = name or f"worker:{uuid4()}"
        self.concurrency = concurrency
        self.redelivery_timeout = redelivery_timeout
        self.reconnection_delay = reconnection_delay
        self.minimum_check_interval = minimum_check_interval

    async def __aenter__(self) -> Self:
        self._heartbeat_task = asyncio.create_task(self._heartbeat())
        self._execution_counts = {}
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del self._execution_counts

        self._heartbeat_task.cancel()
        try:
            await self._heartbeat_task
        except asyncio.CancelledError:
            pass
        del self._heartbeat_task

    def labels(self) -> Mapping[str, str]:
        return {
            **self.docket.labels(),
            "docket.worker": self.name,
        }

    def _log_context(self) -> Mapping[str, str]:
        return {
            **self.labels(),
            "docket.queue_key": self.docket.queue_key,
            "docket.stream_key": self.docket.stream_key,
        }

    @classmethod
    async def run(
        cls,
        docket_name: str = "docket",
        url: str = "redis://localhost:6379/0",
        name: str | None = None,
        concurrency: int = 10,
        redelivery_timeout: timedelta = timedelta(minutes=5),
        reconnection_delay: timedelta = timedelta(seconds=5),
        minimum_check_interval: timedelta = timedelta(milliseconds=100),
        until_finished: bool = False,
        metrics_port: int | None = None,
        tasks: list[str] = ["docket.tasks:standard_tasks"],
    ) -> None:
        with metrics_server(port=metrics_port):
            async with Docket(name=docket_name, url=url) as docket:
                for task_path in tasks:
                    docket.register_collection(task_path)

                async with Worker(
                    docket=docket,
                    name=name,
                    concurrency=concurrency,
                    redelivery_timeout=redelivery_timeout,
                    reconnection_delay=reconnection_delay,
                    minimum_check_interval=minimum_check_interval,
                ) as worker:
                    if until_finished:
                        await worker.run_until_finished()
                    else:
                        await worker.run_forever()  # pragma: no cover

    async def run_until_finished(self) -> None:
        """Run the worker until there are no more tasks to process."""
        return await self._run(forever=False)

    async def run_forever(self) -> None:
        """Run the worker indefinitely."""
        return await self._run(forever=True)  # pragma: no cover

    _execution_counts: dict[str, int]

    async def run_at_most(self, iterations_by_key: Mapping[str, int]) -> None:
        """
        Run the worker until there are no more tasks to process, but limit specified
        task keys to a maximum number of iterations.

        This is particularly useful for testing self-perpetuating tasks that would
        otherwise run indefinitely.

        Args:
            iterations_by_key: Maps task keys to their maximum allowed executions
        """
        self._execution_counts = {key: 0 for key in iterations_by_key}

        def has_reached_max_iterations(execution: Execution) -> bool:
            key = execution.key

            if key not in iterations_by_key:
                return False

            if self._execution_counts[key] >= iterations_by_key[key]:
                return True

            return False

        self.docket.strike_list.add_condition(has_reached_max_iterations)
        try:
            await self.run_until_finished()
        finally:
            self.docket.strike_list.remove_condition(has_reached_max_iterations)
            self._execution_counts = {}

    async def _run(self, forever: bool = False) -> None:
        logger.info("Starting worker %r with the following tasks:", self.name)
        for task_name, task in self.docket.tasks.items():
            signature = inspect.signature(task)
            logger.info("* %s%s", task_name, signature)

        while True:
            try:
                return await self._worker_loop(forever=forever)
            except redis.exceptions.ConnectionError:
                REDIS_DISRUPTIONS.add(1, self.labels())
                logger.warning(
                    "Error connecting to redis, retrying in %s...",
                    self.reconnection_delay,
                    exc_info=True,
                )
                await asyncio.sleep(self.reconnection_delay.total_seconds())

    async def _worker_loop(self, forever: bool = False):
        async with self.docket.redis() as redis:
            stream_due_tasks: _stream_due_tasks = cast(
                _stream_due_tasks,
                redis.register_script(
                    # Lua script to atomically move scheduled tasks to the stream
                    # KEYS[1]: queue key (sorted set)
                    # KEYS[2]: stream key
                    # ARGV[1]: current timestamp
                    # ARGV[2]: docket name prefix
                    """
                local total_work = redis.call('ZCARD', KEYS[1])
                local due_work = 0

                if total_work > 0 then
                    local tasks = redis.call('ZRANGEBYSCORE', KEYS[1], 0, ARGV[1])

                    for i, key in ipairs(tasks) do
                        local hash_key = ARGV[2] .. ":" .. key
                        local task_data = redis.call('HGETALL', hash_key)

                        if #task_data > 0 then
                            local task = {}
                            for j = 1, #task_data, 2 do
                                task[task_data[j]] = task_data[j+1]
                            end

                            redis.call('XADD', KEYS[2], '*',
                                'key', task['key'],
                                'when', task['when'],
                                'function', task['function'],
                                'args', task['args'],
                                'kwargs', task['kwargs'],
                                'attempt', task['attempt']
                            )
                            redis.call('DEL', hash_key)
                            due_work = due_work + 1
                        end
                    end
                end

                if due_work > 0 then
                    redis.call('ZREMRANGEBYSCORE', KEYS[1], 0, ARGV[1])
                end

                return {total_work, due_work}
                """
                ),
            )

            active_tasks: dict[asyncio.Task[None], RedisMessageID] = {}

            async def process_completed_tasks() -> None:
                completed_tasks = {task for task in active_tasks if task.done()}
                for task in completed_tasks:
                    message_id = active_tasks.pop(task)

                    await task

                    async with redis.pipeline() as pipeline:
                        pipeline.xack(
                            self.docket.stream_key,
                            self.docket.worker_group_name,
                            message_id,
                        )
                        pipeline.xdel(
                            self.docket.stream_key,
                            message_id,
                        )
                        await pipeline.execute()

            future_work, due_work = sys.maxsize, 0

            try:
                while forever or future_work or active_tasks:
                    await process_completed_tasks()

                    available_slots = self.concurrency - len(active_tasks)

                    def start_task(
                        message_id: RedisMessageID, message: RedisMessage
                    ) -> None:
                        if not message:  # pragma: no cover
                            return

                        task = asyncio.create_task(self._execute(message))
                        active_tasks[task] = message_id

                        nonlocal available_slots, future_work
                        available_slots -= 1
                        future_work += 1

                    if available_slots <= 0:
                        await asyncio.sleep(self.minimum_check_interval.total_seconds())
                        continue

                    future_work, due_work = await stream_due_tasks(
                        keys=[self.docket.queue_key, self.docket.stream_key],
                        args=[datetime.now(timezone.utc).timestamp(), self.docket.name],
                    )
                    if due_work > 0:
                        logger.debug(
                            "Moved %d/%d due tasks from %s to %s",
                            due_work,
                            future_work,
                            self.docket.queue_key,
                            self.docket.stream_key,
                            extra=self._log_context(),
                        )

                    redeliveries: RedisMessages
                    _, redeliveries, *_ = await redis.xautoclaim(
                        name=self.docket.stream_key,
                        groupname=self.docket.worker_group_name,
                        consumername=self.name,
                        min_idle_time=int(
                            self.redelivery_timeout.total_seconds() * 1000
                        ),
                        start_id="0-0",
                        count=available_slots,
                    )

                    for message_id, message in redeliveries:
                        start_task(message_id, message)

                    if available_slots <= 0:
                        continue

                    new_deliveries: RedisReadGroupResponse = await redis.xreadgroup(
                        groupname=self.docket.worker_group_name,
                        consumername=self.name,
                        streams={self.docket.stream_key: ">"},
                        block=(
                            int(self.minimum_check_interval.total_seconds() * 1000)
                            if forever or active_tasks
                            else None
                        ),
                        count=available_slots,
                    )
                    for _, messages in new_deliveries:
                        for message_id, message in messages:
                            start_task(message_id, message)

            except asyncio.CancelledError:
                if active_tasks:  # pragma: no cover
                    logger.info(
                        "Shutdown requested, finishing %d active tasks...",
                        len(active_tasks),
                        extra=self._log_context(),
                    )
            finally:
                if active_tasks:
                    await asyncio.gather(*active_tasks, return_exceptions=True)
                    await process_completed_tasks()

    async def _execute(self, message: RedisMessage) -> None:
        log_context: Mapping[str, str | float] = self._log_context()

        function_name = message[b"function"].decode()
        function = self.docket.tasks.get(function_name)
        if function is None:
            logger.warning(
                "Task function %r not found", function_name, extra=log_context
            )
            return

        execution = Execution.from_message(function, message)

        async with self.docket.redis() as redis:
            await redis.delete(self.docket.known_task_key(execution.key))

        log_context = {**log_context, **execution.specific_labels()}
        counter_labels = {**self.labels(), **execution.general_labels()}

        arrow = "↬" if execution.attempt > 1 else "↪"
        call = execution.call_repr()

        if self.docket.strike_list.is_stricken(execution):
            arrow = "🗙"
            logger.warning("%s %s", arrow, call, extra=log_context)
            TASKS_STRICKEN.add(1, counter_labels | {"docket.where": "worker"})
            return

        if execution.key in self._execution_counts:
            self._execution_counts[execution.key] += 1

        dependencies = self._get_dependencies(execution)

        context = propagate.extract(message, getter=message_getter)
        initiating_context = trace.get_current_span(context).get_span_context()
        links = [trace.Link(initiating_context)] if initiating_context.is_valid else []

        start = datetime.now(timezone.utc)
        punctuality = start - execution.when
        log_context = {**log_context, "punctuality": punctuality.total_seconds()}
        duration = timedelta(0)

        TASKS_STARTED.add(1, counter_labels)
        TASKS_RUNNING.add(1, counter_labels)
        TASK_PUNCTUALITY.record(punctuality.total_seconds(), counter_labels)

        logger.info("%s [%s] %s", arrow, punctuality, call, extra=log_context)

        try:
            with tracer.start_as_current_span(
                execution.function.__name__,
                kind=trace.SpanKind.CONSUMER,
                attributes={
                    **self.labels(),
                    **execution.specific_labels(),
                    "code.function.name": execution.function.__name__,
                },
                links=links,
            ):
                await execution.function(
                    *execution.args,
                    **{
                        **execution.kwargs,
                        **dependencies,
                    },
                )

            TASKS_SUCCEEDED.add(1, counter_labels)
            duration = datetime.now(timezone.utc) - start
            log_context["duration"] = duration.total_seconds()
            rescheduled = await self._perpetuate_if_requested(
                execution, dependencies, duration
            )
            arrow = "↫" if rescheduled else "↩"
            logger.info("%s [%s] %s", arrow, duration, call, extra=log_context)
        except Exception:
            TASKS_FAILED.add(1, counter_labels)
            duration = datetime.now(timezone.utc) - start
            log_context["duration"] = duration.total_seconds()
            retried = await self._retry_if_requested(execution, dependencies)
            if not retried:
                retried = await self._perpetuate_if_requested(
                    execution, dependencies, duration
                )
            arrow = "↫" if retried else "↩"
            logger.exception("%s [%s] %s", arrow, duration, call, extra=log_context)
        finally:
            TASKS_RUNNING.add(-1, counter_labels)
            TASKS_COMPLETED.add(1, counter_labels)
            TASK_DURATION.record(duration.total_seconds(), counter_labels)

    def _get_dependencies(
        self,
        execution: Execution,
    ) -> dict[str, Any]:
        from .dependencies import get_dependency_parameters

        parameters = get_dependency_parameters(execution.function)

        dependencies: dict[str, Any] = {}

        for parameter_name, dependency in parameters.items():
            # If the argument is already provided, skip it, which allows users to call
            # the function directly with the arguments they want.
            if parameter_name in execution.kwargs:
                dependencies[parameter_name] = execution.kwargs[parameter_name]
                continue

            dependencies[parameter_name] = dependency(self.docket, self, execution)

        return dependencies

    async def _retry_if_requested(
        self,
        execution: Execution,
        dependencies: dict[str, Any],
    ) -> bool:
        from .dependencies import Retry

        retries = [retry for retry in dependencies.values() if isinstance(retry, Retry)]
        if not retries:
            return False

        retry = retries[0]

        if retry.attempts is None or execution.attempt < retry.attempts:
            execution.when = datetime.now(timezone.utc) + retry.delay
            execution.attempt += 1
            await self.docket.schedule(execution)

            TASKS_RETRIED.add(1, {**self.labels(), **execution.specific_labels()})
            return True

        return False

    async def _perpetuate_if_requested(
        self, execution: Execution, dependencies: dict[str, Any], duration: timedelta
    ) -> bool:
        from .dependencies import Perpetual

        perpetuals = [
            perpetual
            for perpetual in dependencies.values()
            if isinstance(perpetual, Perpetual)
        ]
        if not perpetuals:
            return False

        perpetual = perpetuals[0]

        if perpetual.cancelled:
            return False

        now = datetime.now(timezone.utc)
        execution.when = max(now, now + perpetual.every - duration)
        execution.args = perpetual.args
        execution.kwargs = perpetual.kwargs

        await self.docket.schedule(execution)

        TASKS_PERPETUATED.add(1, {**self.labels(), **execution.specific_labels()})
        return True

    @property
    def workers_set(self) -> str:
        return self.docket.workers_set

    def worker_tasks_set(self, worker_name: str) -> str:
        return self.docket.worker_tasks_set(worker_name)

    def task_workers_set(self, task_name: str) -> str:
        return self.docket.task_workers_set(task_name)

    async def _heartbeat(self) -> None:
        while True:
            await asyncio.sleep(self.docket.heartbeat_interval.total_seconds())
            try:
                now = datetime.now(timezone.utc).timestamp()
                maximum_age = (
                    self.docket.heartbeat_interval * self.docket.missed_heartbeats
                )
                oldest = now - maximum_age.total_seconds()

                task_names = list(self.docket.tasks)

                async with self.docket.redis() as r:
                    async with r.pipeline() as pipeline:
                        pipeline.zremrangebyscore(self.workers_set, 0, oldest)
                        pipeline.zadd(self.workers_set, {self.name: now})

                        for task_name in task_names:
                            task_workers_set = self.task_workers_set(task_name)
                            pipeline.zremrangebyscore(task_workers_set, 0, oldest)
                            pipeline.zadd(task_workers_set, {self.name: now})

                        pipeline.sadd(self.worker_tasks_set(self.name), *task_names)
                        pipeline.expire(
                            self.worker_tasks_set(self.name),
                            max(maximum_age, timedelta(seconds=1)),
                        )

                        await pipeline.execute()

                    async with r.pipeline() as pipeline:
                        pipeline.xlen(self.docket.stream_key)
                        pipeline.zcount(self.docket.queue_key, 0, now)
                        pipeline.zcount(self.docket.queue_key, now, "+inf")

                        (
                            stream_depth,
                            overdue_depth,
                            schedule_depth,
                        ) = await pipeline.execute()

                        QUEUE_DEPTH.set(
                            stream_depth + overdue_depth, self.docket.labels()
                        )
                        SCHEDULE_DEPTH.set(schedule_depth, self.docket.labels())

            except asyncio.CancelledError:  # pragma: no cover
                return
            except redis.exceptions.ConnectionError:
                REDIS_DISRUPTIONS.add(1, self.labels())
                logger.exception(
                    "Error sending worker heartbeat",
                    exc_info=True,
                    extra=self._log_context(),
                )
            except Exception:
                logger.exception(
                    "Error sending worker heartbeat",
                    exc_info=True,
                    extra=self._log_context(),
                )
