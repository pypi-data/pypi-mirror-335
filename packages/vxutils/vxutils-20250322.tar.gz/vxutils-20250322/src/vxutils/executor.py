"""Implements a dynamic thread pool executor."""

__author__ = "vex1023 (libao@vxquant.com)"
from contextlib import suppress
import os
import time
import uuid
import logging
import itertools
from datetime import datetime, timedelta
import threading
from enum import Enum
from heapq import heappop, heappush
from concurrent.futures import Future
from queue import Empty
from typing import (
    Any,
    Callable,
    List,
    Optional,
    Tuple,
    Generator,
    Dict,
    Literal,
    Iterator,
)
from functools import wraps
from typing_extensions import Annotated, no_type_check
from pydantic import Field, PlainValidator
from vxutils.convertors import to_datetime, to_enum, to_json
from vxutils.context import VXContext
from vxutils.datamodel.core import VXDataModel

__all__ = [
    "VXTrigger",
    "ONCE",
    "EVERY",
    "DAILY",
    "TriggerStatus",
    "VXTaskItem",
    "VXThreadPoolExecutor",
    "VXTaskQueue",
    "async_task",
    "async_map",
    "run_every",
]
_delta = 0.001


class TriggerStatus(Enum):
    """事件状态"""

    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETE = "COMPLETE"
    UNKNOWN = "UNKNOWN"


class VXTrigger(VXDataModel):
    trigger_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    trigger_dt: Annotated[datetime, PlainValidator(to_datetime)] = Field(
        default_factory=datetime.now
    )
    interval: float = 0

    start_dt: Annotated[datetime, PlainValidator(to_datetime)] = Field(
        default_factory=datetime.now
    )
    end_dt: Annotated[datetime, PlainValidator(to_datetime)] = Field(
        default=datetime.max
    )
    status: Annotated[
        TriggerStatus, PlainValidator(lambda v: to_enum(v, TriggerStatus.PENDING))
    ] = TriggerStatus.PENDING

    @no_type_check
    def model_post_init(self, __context: Any) -> None:
        if self.start_dt > self.end_dt:
            raise ValueError("开始时间不能大于结束时间")

        if self.status != TriggerStatus.PENDING:
            return
        return super().model_post_init(__context)

    def __lt__(self, other: "VXTrigger") -> bool:
        return self.trigger_dt < other.trigger_dt

    def _get_first_trigger_dt(self) -> Tuple[datetime, TriggerStatus]:
        if self.interval == 0:
            return self.start_dt, TriggerStatus.RUNNING

        if self.end_dt < datetime.now() + timedelta(_delta):
            return datetime.max, TriggerStatus.COMPLETE

        if self.start_dt > datetime.now() + timedelta(_delta):
            return self.start_dt, TriggerStatus.RUNNING

        trigger_dt = datetime.fromtimestamp(
            self.start_dt.timestamp()
            + self.interval
            * ((time.time() - self.start_dt.timestamp()) // self.interval + 1)
        )
        if trigger_dt > self.end_dt:
            return datetime.max, TriggerStatus.COMPLETE
        else:
            return trigger_dt, TriggerStatus.RUNNING

    def _get_next_trigger_dt(self) -> Tuple[datetime, TriggerStatus]:
        if self.interval == 0 or self.status == TriggerStatus.COMPLETE:
            return datetime.max, TriggerStatus.COMPLETE

        trigger_dt = self.trigger_dt + timedelta(seconds=self.interval)
        if self.trigger_dt + timedelta(seconds=self.interval) > (
            self.end_dt - timedelta(seconds=_delta)
        ):
            return datetime.max, TriggerStatus.COMPLETE
        else:
            return trigger_dt, TriggerStatus.RUNNING

    def __next__(self) -> "VXTrigger":
        if self.status == TriggerStatus.PENDING:
            self.trigger_dt, self.status = self._get_first_trigger_dt()
        elif self.status == TriggerStatus.RUNNING:
            self.trigger_dt, self.status = self._get_next_trigger_dt()
        if self.status == TriggerStatus.COMPLETE:
            raise StopIteration

        return self

    def __iter__(self) -> Generator[Tuple[str, Any], None, None]:
        return self  # type: ignore[return-value]

    @classmethod
    @no_type_check
    def once(cls, trigger_dt: Optional[datetime] = None) -> "VXTrigger":
        """一次性执行的触发器

        Keyword Arguments:
            trigger_dt {Optional[datetime]} -- 触发时间 (default: {None})

        Returns:
            VXTrigger -- _description_
        """
        if trigger_dt is None:
            trigger_dt = datetime.now()
        data = {
            "status": "Pending",
            "trigger_dt": trigger_dt,
            "start_dt": trigger_dt,
            "end_dt": trigger_dt,
            "interval": 0,
            "skip_holiday": False,
        }
        return cls(**data)

    @classmethod
    @no_type_check
    def every(
        cls,
        interval: float,
        *,
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None,
        skip_holiday: bool = False,
    ) -> "VXTrigger":
        """每隔一段时间执行的触发器

        Arguments:
            interval {float} -- 间隔时间，单位：秒

        Keyword Arguments:
            start_dt {Optional[datetime]} -- 开始时间 (default: {None})
            end_dt {Optional[datetime]} -- 结束时间 (default: {None})
            skip_holiday {bool} -- 是否跳过假期 (default: {False})

        Returns:
            VXTrigger -- _description_
        """
        if not start_dt:
            start_dt = datetime.now()
        if not end_dt:
            end_dt = datetime.max
        data = {
            "status": "Pending",
            "trigger_dt": start_dt,
            "start_dt": start_dt,
            "end_dt": end_dt,
            "interval": interval,
            "skip_holiday": skip_holiday,
        }
        return cls(**data)

    @classmethod
    @no_type_check
    def daily(
        cls,
        timestr: str = "00:00:00",
        freq: int = 1,
        *,
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None,
        skip_holiday: bool = False,
    ) -> "VXTrigger":
        """创建每日执行的触发器

        Keyword Arguments:
            timestr {str} -- 时间点 (default: {"00:00:00"})
            freq {int} -- 日期间隔，单位：天 (default: {1})
            start_dt {Optional[VXDatetime]} -- 开始时间 (default: {None})
            end_dt {Optional[VXDatetime]} -- 结束事件 (default: {None})
            skip_holiday {bool} -- 是否跳过工作日 (default: {False})

        Returns:
            VXTrigger -- 触发器
        """
        if not start_dt:
            start_dt = datetime.now()
        if not end_dt:
            end_dt = datetime.max
        data = {
            "status": "Pending",
            "trigger_dt": start_dt,
            "start_dt": start_dt.combine(
                start_dt.date(), datetime.strptime(timestr, "%H:%M:%S").time()
            ),
            "end_dt": end_dt,
            "interval": 86400 * freq,
            "skip_holiday": skip_holiday,
        }

        return cls(**data)


ONCE = VXTrigger.once
EVERY = VXTrigger.every
DAILY = VXTrigger.daily


class VXTaskItem:
    def __init__(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.future: Future[Any] = Future()
        self.task_id = uuid.uuid4().hex[16]

    def __call__(self, context: Optional[VXContext] = None) -> None:
        if not self.future.set_running_or_notify_cancel():
            return

        try:
            if context is None:
                result = self.func(*self.args, **self.kwargs)
            else:
                result = self.func(context, *self.args, **self.kwargs)
            self.future.set_result(result)

        except Exception as exc:
            self.future.set_exception(exc)
            logging.error("task error: %s", exc, exc_info=True)

    def __str__(self) -> str:
        json_str = to_json(
            {
                "task_id": self.task_id,
                "func": str(self.func),
                "future": str(self.future),
            }
        )
        return f"<{self.__class__.__name__}: {json_str}>"


class VXTaskQueue:
    """Create a queue object with infinite size."""

    def __init__(self):
        self._queue: List[Tuple[VXTrigger, Any]] = []
        # mutex must be held whenever the queue is mutating.  All methods
        # that acquire mutex must release it before returning.  mutex
        # is shared between the three conditions, so acquiring and
        # releasing the conditions also acquires and releases mutex.
        self.mutex = threading.Lock()
        # Notify not_empty whenever an item is added to the queue; a
        # thread waiting to get is notified then.
        self.not_empty = threading.Condition(self.mutex)

    @property
    def queue(self) -> List[Tuple[VXTrigger, Any]]:
        return self._queue

    def qsize(self):
        """Return the approximate size of the queue (not reliable!)."""
        with self.mutex:
            return self._qsize()

    def empty(self):
        """Return True if the queue is empty, False otherwise (not reliable!).

        This method is likely to be removed at some point.  Use qsize() == 0
        as a direct substitute, but be aware that either approach risks a race
        condition where a queue can grow before the result of empty() or
        qsize() can be used.

        To create code that needs to wait for all queued tasks to be
        completed, the preferred technique is to use the join() method.
        """
        with self.mutex:
            return not self._qsize()

    def put(self, task: VXTaskItem, trigger: Optional[VXTrigger] = None) -> None:
        """Put an item into the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until a free slot is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Full exception if no free slot was available within that time.
        Otherwise ('block' is false), put an item on the queue if a free slot
        is immediately available, else raise the Full exception ('timeout'
        is ignored in that case).

        Raises ShutDown if the queue has been shut down.
        """

        if trigger is None:
            trigger = ONCE()

        with self.mutex:
            self._put(task, trigger)
            self.not_empty.notify()

    def get(self, block=True, timeout=None) -> VXTaskItem:
        """Remove and return an item from the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until an item is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Empty exception if no item was available within that time.
        Otherwise ('block' is false), return an item if one is immediately
        available, else raise the Empty exception ('timeout' is ignored
        in that case).

        Raises ShutDown if the queue has been shut down and is empty,
        or if the queue has been shut down immediately.
        """
        with self.not_empty:
            if not block and (not self._qsize()):
                raise Empty

            if timeout is not None and timeout <= 0:
                raise ValueError("'timeout' must be a non-negative number")

            if timeout is not None:
                endtime = time.time() + timeout
            else:
                endtime = float("inf")

            while not self._qsize():
                now = time.time()
                if now >= endtime:
                    raise Empty

                lastest_trigger_dt = (
                    endtime
                    if len(self.queue) == 0
                    else self.queue[0][0].trigger_dt.timestamp()
                )
                min_endtime = min(endtime, lastest_trigger_dt, now + 10)
                remaining = min_endtime - now
                self.not_empty.wait(remaining)
            item = self._get()
            return item

    def get_nowait(self) -> VXTaskItem:
        """Remove and return an item from the queue without blocking.

        Only get an item if one is immediately available. Otherwise
        raise the Empty exception.
        """
        return self.get(block=False)

    def _qsize(self) -> int:
        now = datetime.now()
        return len([1 for t, e in self.queue if t.trigger_dt <= now])

    # Put a new item in the queue
    def _put(self, item: VXTaskItem, trigger: VXTrigger) -> None:
        with suppress(StopIteration):
            next(trigger)
            heappush(self.queue, (trigger, item))

    # Get an item from the queue
    def _get(self) -> VXTaskItem:
        trigger, task = heappop(self.queue)
        if trigger.status == TriggerStatus.RUNNING and task is not None:
            new_task = VXTaskItem(task.func, *task.args, **task.kwargs)
            self._put(new_task, trigger)
            self.not_empty.notify()
        return task


def _result_or_cancel(fut: Future[Any], timeout: Optional[float] = None) -> None:
    """
    尝试获取Future的结果，如果超时则取消Future。

    参数:
        fut (Future[Any]): 要获取结果的Future对象。
        timeout (Optional[float]): 等待结果的超时时间，默认为None（无超时）。

    返回:
        None: 此函数不返回任何值。

    异常:
        无: 此函数不抛出任何异常，但会处理Future对象的异常。

    注意:
        此函数会在获取结果后取消Future，以避免资源泄漏。
    """
    try:
        try:
            return fut.result(timeout)
        finally:
            fut.cancel()
    finally:
        # Break a reference cycle with the exception in self._exception
        del fut


class VXThreadPoolExecutor:
    """动态线程池"""

    _counter = itertools.count().__next__

    def __init__(
        self,
        idle_timeout: float = 600,
        context: Optional[VXContext] = None,
        worker_func: Callable[["VXThreadPoolExecutor", VXContext], None] = None,
    ) -> None:
        self._max_workers = min(32, (os.cpu_count() or 1) + 4)
        self._context = context
        self._taskqueue = VXTaskQueue()
        # 用于通知线程退出的事件
        self._stop_event = threading.Event()
        # 用于记录workers的是否空闲, True 表示线程当前空闲，False 表示线程当前正在工作中...
        self._workers: Dict[threading.Thread, bool] = {}
        self._idle_timeout = idle_timeout
        if worker_func is not None:
            self._worker_run = worker_func

    def set_context(self, context: VXContext) -> None:
        """设置上下文

        Arguments:
            context -- 上下文
        """
        self._context = context

    def __enter__(self) -> "VXThreadPoolExecutor":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.shutdown(wait=True)

    def _worker_run(self, context: Optional[VXContext] = None):
        try:
            while not self._stop_event.is_set():
                try:
                    # 如果当前线程空闲，则从队列中获取任务，否则从队列中获取任务
                    if self._workers[threading.current_thread()] is True:
                        task = self._taskqueue.get(timeout=self._idle_timeout)
                    else:
                        task = self._taskqueue.get_nowait()

                    if task is None:
                        break
                    self._workers[threading.current_thread()] = False
                    task(context)
                except Empty:
                    # 如果当前线程空闲且当前空闲线程超过2个时，本线程退出
                    if sum(self._workers.values()) > 2:
                        break
                    self._workers[threading.current_thread()] = True
        finally:
            self._workers.pop(threading.current_thread(), None)

    def _adjust_workers(self) -> None:
        """调整工作线程数量"""
        # 如果工作线程中有空闲的线程或者workers 已达到上限，则无需增加worker
        if len(self._workers) >= self._max_workers or any(self._workers.values()):
            time.sleep(0)
            return

        t = threading.Thread(
            name=f"Worker[{self._counter()}]",
            daemon=True,
            target=self._worker_run,
            kwargs={"context": self._context},
        )
        self._workers[t] = False
        t.start()

    def submit(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Future[Any]:
        """提交即时运行任务

        Arguments:
            func -- 任务

        Returns:
            Future[Any]
        """
        task = VXTaskItem(func, *args, **kwargs)
        self.crontab(task)
        return task.future

    def map(
        self,
        fn: Callable[..., Any],
        *iterables: Iterator[Any],
        timeout: Optional[float] = None,
        chunksize: int = 1,
    ) -> Generator[None, Any, None]:
        """Returns an iterator equivalent to map(fn, iter).

        Args:
            fn: A callable that will take as many arguments as there are
                passed iterables.
            timeout: The maximum number of seconds to wait. If None, then there
                is no limit on the wait time.
            chunksize: The size of the chunks the iterable will be broken into
                before being passed to a child process. This argument is only
                used by ProcessPoolExecutor; it is ignored by
                ThreadPoolExecutor.

        Returns:
            An iterator equivalent to: map(func, *iterables) but the calls may
            be evaluated out-of-order.

        Raises:
            TimeoutError: If the entire result iterator could not be generated
                before the given timeout.
            Exception: If fn(*args) raises for any values.
        """
        if timeout is not None:
            end_time = timeout + time.monotonic()

        fs = [self.submit(fn, *args) for args in zip(*iterables)]

        # Yield must be hidden in closure so that the futures are submitted
        # before the first iterator value is required.
        def result_iterator() -> Generator[None, Any, None]:
            try:
                # reverse to keep finishing order
                fs.reverse()
                while fs:
                    # Careful not to keep a reference to the popped future
                    if timeout is None:
                        yield _result_or_cancel(fs.pop())
                    else:
                        yield _result_or_cancel(fs.pop(), end_time - time.monotonic())
            finally:
                for future in fs:
                    future.cancel()

        return result_iterator()

    def crontab(self, task: VXTaskItem, /, trigger: Optional[VXTrigger] = None) -> None:
        """调度任务

        Arguments:
            task -- 任务
            trigger -- 触发器 (default: {None})
        """
        self._taskqueue.put(task, trigger)
        self._adjust_workers()

    def shutdown(self, wait: bool = True) -> None:
        """关闭任务执行器

        Keyword Arguments:
            wait -- 是否等待任务完成 (default: {True})
        """
        self._stop_event.set()
        workers = list(self._workers.keys())
        for t in workers:
            self._taskqueue.put(None)

        if wait:
            for t in workers:
                if t.is_alive():
                    t.join()

        self._workers.clear()


class async_task:
    """
    多线程提交任务
    example::

        @async_task
        def test():
            time.sleep(1)
    """

    __executor__ = VXThreadPoolExecutor(idle_timeout=600)

    def __init__(
        self,
        max_workers: int = 5,
        on_error: Literal["logging", "raise", "ignore"] = "raise",
    ) -> None:
        self._semaphore = threading.Semaphore(max_workers)
        self._on_error = on_error

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        def semaphore_func(*args: Any, **kwargs: Any) -> Any:
            with self._semaphore:
                try:
                    return func(*args, **kwargs)
                except Exception as err:
                    if self._on_error == "logging":
                        logging.error(
                            "async_task error: %s",
                            err,
                            exc_info=True,
                            stack_info=True,
                        )
                    elif self._on_error == "raise":
                        raise err from err
                    return None

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Future[Any]:
            return self.__executor__.submit(semaphore_func, *args, **kwargs)

        return wrapper


def async_map(
    func: Callable[..., Any],
    *iterables: Any,
    timeout: Optional[float] = None,
    chunsize: int = 1,
) -> Any:
    """异步map提交任务

    Arguments:
        func {Callable[..., Any]} -- 运行func

    Returns:
        Any -- 返回值
    """
    return async_task.__executor__.map(
        func, *iterables, timeout=timeout, chunksize=chunsize
    )


def run_every(
    func: Callable[[Any], Any],
    interval: float,
    *args: Any,
    start_dt: Optional[datetime] = None,
    end_dt: Optional[datetime] = None,
    **kwargs: Any,
) -> None:
    """每隔一段时间运行任务

    Arguments:
        func {Callable[..., Any]} -- 运行func
        interval {float} -- 时间间隔

    Keyword Arguments:
        start_dt {Optional[datetime]} -- 开始时间 (default: {None})
        end_dt {Optional[datetime]} -- 结束时间 (default: {None})
    """
    trigger = VXTrigger.every(interval, start_dt=start_dt, end_dt=end_dt)
    task = VXTaskItem(func, *args, **kwargs)
    async_task.__executor__.crontab(
        task,
        trigger=trigger,
    )


def delay(
    func: Callable[..., Any],
    *args: Any,
    delay: float = 0,
    **kwargs: Any,
) -> Future[Any]:
    """延迟运行任务

    Arguments:
        func {Callable[..., Any]} -- 运行func
        delay {float} -- 延迟时间

    Returns:
        Any -- 返回值
    """
    trigger = VXTrigger.once(datetime.now() + timedelta(seconds=delay))
    task = VXTaskItem(func, *args, **kwargs)
    async_task.__executor__.crontab(
        task,
        trigger=trigger,
    )
    return task.future


if __name__ == "__main__":
    trigger = DAILY("08:30:00")
    cnt = 0
    for t in trigger:
        print(t.trigger_dt)
        cnt += 1
        if cnt > 10:
            break

    with VXThreadPoolExecutor() as executor:
        executor.submit(print, "hello world")
        # executor.crontab(
        #    print, "hello world", trigger=ONCE(datetime.now() + timedelta(seconds=1))
        # )
        executor.crontab(VXTaskItem(print, "hello world2"), trigger=EVERY(interval=1))
        list(executor.map(print, [1, 2, 3, 4, 5]))
    print("=" * 60)

    @async_task()
    def test(n: int) -> None:
        time.sleep(n / 10)
        print(datetime.now(), "==>", n)

    time.sleep(10)
