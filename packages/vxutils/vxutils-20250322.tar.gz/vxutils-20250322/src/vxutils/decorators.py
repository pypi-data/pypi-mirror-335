# endcoding = utf-8
"""
author : vex1023
email :  vex1023@qq.com
各类型的decorator
"""

import signal
import time
import logging

from typing import (
    Callable,
    Tuple,
    Any,
    Type,
    Literal,
    Deque,
    Optional,
    Dict,
    Union,
)

from functools import wraps


import inspect
from datetime import datetime, timedelta

import pickle
from pathlib import Path
from threading import Lock
from hashlib import sha256
import polars as pl
from vxutils import to_json

__all__ = [
    "retry",
    "timeit",
    "singleton",
    "timeout",
    # "async_task",
    # "async_map",
    "timer",
    # "VXAsyncResult",
    "rate_limit",
    "VXLruCache",
]


###################################
# 错误重试方法实现
# @retry(tries, CatchExceptions=(Exception,), delay=0.01, backoff=2)
###################################


class retry:
    def __init__(
        self,
        tries: int,
        catch_exceptions: Tuple[Type[Exception]],
        delay: float = 0.1,
        backoff: int = 2,
    ) -> None:
        """重试装饰器

        Arguments:
            tries {int} -- 重试次数
            cache_exceptions {Union[Exception, Sequence[Exception]]} -- 发生错误时，需要重试的异常列表

        Keyword Arguments:
            delay {float} -- 延时时间 (default: {0.1})
            backoff {int} -- 延时时间等待倍数 (default: {2})
        """
        if backoff <= 1:
            raise ValueError("backoff must be greater than 1")

        if tries < 0:
            raise ValueError("tries must be 0 or greater")

        if delay <= 0:
            raise ValueError("delay must be greater than 0")

        self._catch_exceptions: Tuple[Type[Exception]] = (Exception,)
        if catch_exceptions:
            self._catch_exceptions = catch_exceptions

        self._tries = tries
        self._delay = delay
        self._backoff = backoff

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            mdelay = self._delay
            for i in range(1, self._tries):
                try:
                    return func(*args, **kwargs)
                except self._catch_exceptions as err:
                    logging.error(
                        "function %s(%s, %s) try %s times error: %s\n",
                        func.__name__,
                        args,
                        kwargs,
                        i,
                        err,
                    )
                    logging.warning("Retrying in %.4f seconds...", mdelay)

                    time.sleep(mdelay)
                    mdelay *= self._backoff

            return func(*args, **kwargs)

        return wrapper


###################################
# 计算运行消耗时间
# @timeit
###################################


class timer:
    """计时器"""

    def __init__(self, descriptions: str = "", *, warnning: float = 0) -> None:
        self._descriptions = descriptions
        self._start = 0.0
        self._warnning = warnning * 1000
        self._end = 0.0

    @property
    def cost(self) -> float:
        return (
            (time.perf_counter() if self._end == 0 else self._end) - self._start
        ) * 1000

    def __enter__(self) -> "timer":
        logging.debug(f"{self._descriptions} start...")
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self._end = time.perf_counter()

        if self.cost > self._warnning > 0:
            logging.warning(f"{self._descriptions} used : {self.cost:.2f}ms")
        else:
            logging.debug(f"{self._descriptions} used : {self.cost:.2f}ms")


class timeit:
    """
    计算运行消耗时间
    @timeit(0.5)
    def test():
        time.sleep(1)
    """

    def __init__(self, warnning_time: int = 5) -> None:
        self._warnning_time = warnning_time

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with timer(
                f"{func.__name__}({args},{kwargs})", warnning=self._warnning_time
            ):
                return func(*args, **kwargs)

        return wrapper


###################################
# Singleton 实现
# @singleton
###################################


class singleton(object):
    """
    单例
    example::

        @singleton
        class YourClass(object):
            def __init__(self, *args, **kwargs):
                pass
    """

    def __init__(self, cls: Type[Any]) -> None:
        self._instance = None
        self._cls = cls
        self._lock = Lock()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = self._cls(*args, **kwargs)
        return self._instance


###################################
# 限制超时时间
# @timeout(seconds, error_message='Function call timed out')
###################################


# class TimeoutError(Exception):
#    pass


class timeout:
    def __init__(
        self, seconds: float = 1, *, timeout_msg: str = "Function %s call time out."
    ) -> None:
        self._timeout = seconds
        self._timeout_msg = timeout_msg

    def __call__(self, func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            signal.signal(signal.SIGALRM, self._handle_timeout)  # type: ignore[attr-defined]
            signal.alarm(self._timeout)  # type: ignore[attr-defined]
            try:
                return func(*args, **kwargs)
            finally:
                signal.alarm(0)  # type: ignore[attr-defined]

        return wrapper

    def _handle_timeout(self, signum: int, frame: Any) -> None:
        raise TimeoutError(
            f"{self._timeout_msg} after {self._timeout * 1000}ms,{signum},{frame}"
        )


class RateOverLimitError(RuntimeError):
    """"""

    pass


class rate_limit:
    def __init__(
        self,
        limits: int = 1,
        peroid: float = 1.0,
        if_over_limit: Literal["raise", "wait"] = "wait",
    ) -> None:
        self._peroid = peroid
        self._records: Deque[float] = Deque(maxlen=limits)
        self._records.append(0)
        self._if_over_limit = if_over_limit
        self._lock = Lock()

    def __call__(self, func: Callable[..., Any]) -> Any:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with self._lock:
                now = time.perf_counter()
                if self._records[0] > now - self._peroid:
                    if self._if_over_limit == "wait":
                        time.sleep(self._peroid - (now - self._records[0]))
                        now = time.perf_counter()
                    else:
                        raise RateOverLimitError(
                            f"Call limit {self._records.maxlen} times per {self._peroid} seconds"
                        )
                self._records.append(now)
            return func(*args, **kwargs)

        return wrapper


_EMPTY_CACHE_DATA = pl.DataFrame(
    {
        "key": [""],
        "value": [""],
        "expried_dt": [datetime.now()],
        "updated_dt": [datetime.now()],
    },
    schema_overrides={
        "key": pl.Utf8,
        "value": pl.Object,
        "expried_dt": pl.Datetime,
        "updated_dt": pl.Datetime,
    },
).clear()


class MissingCacheError(Exception):
    """缓存缺失"""


class VXTTLCache:
    """缓存"""

    def __init__(self, max_size: int = 0):
        """初始化"""
        self._data = _EMPTY_CACHE_DATA

        if max_size > 0:
            self._max_size = max_size
        else:
            self._max_size = 0
        self._lock = Lock()

    def __len__(self) -> int:
        with self._lock:
            return self._data.shape[0]

    @property
    def data(self) -> pl.DataFrame:
        """缓存数据"""
        with self._lock:
            return self._filter_expried()

    def create_key(self, **keys: Any) -> str:
        """创建缓存键"""
        return sha256(
            to_json(keys, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()

    def __getitem__(self, key: str) -> Any:
        """获取缓存"""
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """设置缓存"""
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        """删除缓存"""
        self.delete(key)

    def _filter_expried(self) -> pl.DataFrame:
        """删除过期缓存"""
        return self._data.filter(pl.col("expried_dt") > datetime.now())

    def get(self, key: str) -> Any:
        """获取缓存"""

        with self._lock:
            self._data = (
                self._filter_expried()
                .with_columns(
                    updated_dt=pl.when(pl.col("key").is_in([key]))
                    .then(datetime.now())
                    .otherwise(pl.col("updated_dt"))
                )
                .sort("updated_dt", descending=True)
            )

            df = self._data.filter(pl.col("key").is_in([key]))
            if df.is_empty():
                raise MissingCacheError(f"Cache {key} not found.")
            return df["value"][0]

    def get_many(self, *keys: str) -> Dict[str, Any]:
        """获取缓存"""
        if len(keys) == 0:
            return {}

        with self._lock:
            self._data = (
                self._filter_expried()
                .with_columns(
                    updated_dt=pl.when(pl.col("key").is_in(keys))
                    .then(datetime.now())
                    .otherwise(pl.col("updated_dt"))
                )
                .sort("updated_dt", descending=True)
            )

            df = self._data.filter(pl.col("key").is_in(keys))
            if df.is_empty():
                raise MissingCacheError(f"Cache {keys} not found.")

            return {row["key"]: row["value"] for row in df.rows(named=True)}

    def set(self, key: str, value: Any, expried_dt: Optional[datetime] = None) -> None:
        """设置缓存"""
        if expried_dt is None:
            expried_dt = datetime.max

        with self._lock:
            self._data = (
                self._filter_expried()
                .filter(pl.col("key") != key)
                .vstack(
                    pl.DataFrame(
                        {
                            "key": [key],
                            "value": [value],
                            "expried_dt": [expried_dt],
                            "updated_dt": [datetime.now()],
                        },
                        schema_overrides={
                            "key": pl.Utf8,
                            "value": pl.Object,
                            "expried_dt": pl.Datetime,
                            "updated_dt": pl.Datetime,
                        },
                    )
                )
                .sort("updated_dt", descending=True)
            )
            if self._max_size > 0 and self._data.shape[0] > self._max_size:
                self._data = self._data.head(self._max_size)

            # print(f"set {key} --> {value}@{expried_dt},{self._data}")

    def delete(self, key: str) -> None:
        """删除缓存"""
        with self._lock:
            self._data = self._data.filter(pl.col("key") != key)

    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            del self._data
            self._data = _EMPTY_CACHE_DATA.clone()

    def dump(
        self, cache_db: Union[str, Path] = Path().home() / ".vxquant/cache.parquet"
    ) -> None:
        """保存缓存"""

        if self._data.is_empty():
            return

        cache_db.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            self._data.select(
                pl.col("key"),
                pl.col("expried_dt"),
                zip_value=pl.col("value").map_elements(
                    pickle.dumps, return_dtype=pl.Binary
                ),
            ).filter(pl.col("zip_value").is_null().not_()).write_parquet(cache_db)

    def load(self, cache_db: Union[str, Path]) -> None:
        """加载缓存"""
        if not cache_db.exists():
            return

        cache_data = pl.read_parquet(cache_db).to_dicts()

        with self._lock:
            self._data = pl.DataFrame(
                {
                    "key": [item["key"] for item in cache_data],
                    "value": [pickle.loads(item["zip_value"]) for item in cache_data],
                    "expried_dt": [item["expried_dt"] for item in cache_data],
                    "updated_dt": [item["updated_dt"] for item in cache_data],
                },
                schema_overrides={
                    "key": pl.Utf8,
                    "value": pl.Object,
                    "expried_dt": pl.Datetime,
                    "updated_dt": pl.Datetime,
                },
            )

    def __call__(self, ttl: float = 0) -> Callable[..., Any]:
        """装饰器"""

        def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
            """装饰器"""

            @wraps(func)
            def inner(*args: Any, **kwargs: Any) -> Any:
                """装饰器"""
                keys = inspect.getcallargs(func, *args, **kwargs)
                keys["__name__"] = func.__name__
                keys["__module__"] = func.__module__
                key = self.create_key(**keys)
                try:
                    return self.get(key)
                except MissingCacheError:
                    value = func(*args, **kwargs)
                    expried_dt = (
                        datetime.now() + timedelta(seconds=ttl)
                        if ttl > 0
                        else datetime.max
                    )
                    self.set(key, value, expried_dt)
                    return value

            return inner

        return wrapper


ttlcache = VXTTLCache()

if __name__ == "__main__":
    from vxutils import loggerConfig
    from contextlib import suppress
    import logging

    loggerConfig()
    ttlcache.set("a", 1, expried_dt=datetime.now() + timedelta(seconds=2))
    ttlcache.set("b", 2)
    print(ttlcache.get("a"))
    print(ttlcache.get("b"))

    # @rate_limit(3, 10)
    @ttlcache(3)
    def test(i: int = 10) -> None:
        print("test", i, ttlcache.data)
        time.sleep(1.2)

    with timer("test timer", warnning=0.001) as t, suppress(RuntimeError):
        for i in range(10):
            test(1)
            time.sleep(0.5)
    print(ttlcache.data)
