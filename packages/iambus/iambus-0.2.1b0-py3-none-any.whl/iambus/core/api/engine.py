import abc
import asyncio
import typing as t
from logging import getLogger

from iambus.core.api.isolation import IsolationManager
from iambus.core.api.typedef import RequestObject
from iambus.core.api.typing import MapReturnType, MessageMapType, MessageType, WrappedHandler

logger = getLogger(__name__)


class BaseQueueWorker(metaclass=abc.ABCMeta):
    """Base queue worker class."""

    def __init__(self, engine: "AbstractEngine", key: t.Optional[t.AnyStr] = None):
        self._engine = engine
        self._name = f'{self._engine.name} (key {key})'
        self._queue = asyncio.Queue[RequestObject]()
        self._started = False

    def tell(self) -> int:
        """Return size of the queue."""
        return self._queue.qsize()

    @abc.abstractmethod
    def start(self) -> None:
        """Start the worker."""

    @abc.abstractmethod
    async def put(self, request: RequestObject) -> None:
        """Put the message to the queue."""

    async def _worker(self):
        while True:
            try:
                logger.debug(f'{self._name} waiting for messages')
                request = await self._queue.get()
                logger.debug(f'{self._name} got message {request.message}')
                handler = self._engine.map.find(request.message)

                try:
                    response = await self._engine.handle(
                        handler,
                        message=request.message,
                        key=request.key,
                    )
                    if request.wait_for_response:
                        request.callback.set_result(response)
                except Exception as exc:
                    if request.wait_for_response:
                        request.callback.set_exception(exc)
                    else:
                        await self._engine.error_handler(exc)

            except asyncio.CancelledError:
                break

            except Exception as e:
                await self._engine.error_handler(e)


class QueueWorker(BaseQueueWorker):
    """Single key-bound queue worker."""

    def start(self):
        """Start the worker."""
        asyncio.create_task(self._worker())
        self._started = True

    async def put(self, request: RequestObject) -> None:
        """Put the message to the queue."""
        if not self._started:
            self.start()

        await self._queue.put(request)


class MultiQueueWorker:
    """Multiple key-bound queue worker."""

    def __init__(self, engine: "AbstractEngine"):
        self._engine = engine
        self._queues = []

    def get_queue(self):
        """Return min tasks queue."""
        return min(self._queues, key=lambda q: q.tell())

    def start(self, workers: int):
        """Start the worker."""
        self._queues = [QueueWorker(self._engine) for _ in range(workers)]

    async def put(self, request: RequestObject) -> None:
        """Put message to the queue."""
        await self.get_queue().put(request)


class AbstractEngine(t.Generic[MessageMapType], metaclass=abc.ABCMeta):
    """Engine protocol.

    Implement:
      - handle
    """

    def __init__(self, message_map: MessageMapType):
        self.map = message_map
        self._default = MultiQueueWorker(self)
        self._topics: dict[t.AnyStr, QueueWorker] = {}
        self._isolation = IsolationManager()

        self._workers: int = 0
        self._name: str = self.__class__.__name__
        self._stop_event = asyncio.Event()
        self._started = False

    name = property(lambda self: self._name)

    @property
    def is_started(self) -> bool:
        """Return True if the engine is started."""
        return self._started

    async def put_to_queue(self, request: RequestObject) -> t.Awaitable[...]:
        """Put the message to the queue."""
        if request.wait_for_response is not True:
            request.callback.set_result(None)

        async with self._isolation.get_lock(ikey=request.isolation_key()):
            if key := request.key:
                # for each key create a queue worker
                await self._topics.setdefault(key, QueueWorker(self, key)).put(request)
            else:
                # put to default if no key presente
                await self._default.put(request)

        return await request.callback

    async def error_handler(self, error: str | Exception) -> None:  # noqa
        """Error handler"""
        logger.exception(error)

    @abc.abstractmethod
    async def handle(
        self,
        handler: MapReturnType,
        /,
        message: MessageType,
        key: t.Optional[t.AnyStr] = None,
    ) -> t.Any:
        """Handler the message. Optionally can return new messages."""

    async def handle_one(
        self,
        handler: WrappedHandler,
        message: MessageType,
        key: t.Optional[t.AnyStr] = None,
    ):
        """Handle one message by one handler."""
        response = await handler.handle(message)
        asyncio.ensure_future(self.handle_side_events(handler, key=key))
        return response

    async def handle_side_events(
        self,
        handler: WrappedHandler,
        key: t.Optional[t.AnyStr] = None,
    ) -> None:
        """Handle side handler event"""
        for event in await handler.dump_events():
            await self.put_to_queue(
                RequestObject(message=event, key=key, wait_for_response=False),
            )

    def start(self, workers: int = 3) -> None:
        """Start the engine."""
        self._default.start(workers)
        self._started = True
