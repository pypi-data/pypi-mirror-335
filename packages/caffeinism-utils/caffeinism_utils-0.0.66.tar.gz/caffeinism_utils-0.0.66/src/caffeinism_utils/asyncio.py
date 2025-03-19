import asyncio
import collections
import contextlib
import inspect
import logging
from abc import ABC
from functools import partial, update_wrapper, wraps

logger = logging.getLogger(__name__)


class Function(ABC):
    def __get__(self, instance, instancetype):
        return partial(self.__call__, instance)


def run_in_threadpool_deco(func):
    @wraps(func)
    def _func(*args, **kwargs):
        return run_in_executor(None, func, *args, **kwargs)

    return _func


def run_in_threadpool(func, *args, **kwargs):
    return run_in_executor(None, func, *args, **kwargs)


def run_in_executor_deco(pool):
    def decorator(func):
        @wraps(func)
        def _func(*args, **kwargs):
            return run_in_executor(pool, func, *args, **kwargs)

        return _func

    return decorator


def run_in_executor(pool, func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    if inspect.isgeneratorfunction(func):
        f = Cancellable(func(*args, **kwargs))
        future = loop.run_in_executor(pool, f)
        return CancellableFuture(future, f.cancel, loop=loop)
    else:
        return loop.run_in_executor(pool, partial(func, *args, **kwargs))


class Cancellable:
    def __init__(self, generator):
        self.generator = generator
        self.cancelled = False

    def __call__(self):
        try:
            while True:
                next(self.generator)
                if self.cancelled:
                    raise asyncio.CancelledError
        except StopIteration as e:
            return e.value

    def cancel(self):
        self.cancelled = True


class CancellableFuture(asyncio.Future):
    def __init__(self, future: asyncio.Future, cancel_func, *, loop=None):
        super().__init__(loop=loop)
        self.__future = future
        self.__cancel_func = cancel_func
        self.__future.add_done_callback(self.__future_done)

    def __future_done(self, fut: asyncio.Future):
        exc = fut.exception()
        if exc is not None:
            self.set_exception(exc)
            return

        self.set_result(self.__future.result())

    def cancel(self, msg=None):
        self.__cancel_func()
        self.__future.cancel(msg=msg)
        return super().cancel(msg=msg)


class LastManStanding:
    class __Defeat(Exception):
        pass

    def __init__(self):
        self.__locks = collections.defaultdict(asyncio.Lock)
        self.__counter = collections.defaultdict(int)

    @contextlib.asynccontextmanager
    async def join(self, key):
        with contextlib.suppress(LastManStanding.__Defeat):
            yield self.__wait(key)

    @contextlib.asynccontextmanager
    async def __wait(self, key):
        self.__counter[key] += 1
        async with self.__locks[key]:
            self.__counter[key] -= 1
            if self.__counter[key]:
                raise LastManStanding.__Defeat
            else:
                yield


class SynchronousQueue(object):
    def __init__(self):
        self._queue = asyncio.Queue(1)
        self._lock = asyncio.Lock()

    def done(self):
        self._queue.task_done()

    async def get(self):
        return await self._queue.get()

    async def put(self, item):
        async with self._lock:
            await self._queue.put(item)
            await self._queue.join()
