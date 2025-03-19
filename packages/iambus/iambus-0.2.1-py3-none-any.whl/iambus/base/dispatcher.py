import inspect
import typing as t
from logging import getLogger
from typing import Optional

from iambus.base.routers.eventrouter import EventRouter
from iambus.base.routers.requestrouter import RequestRouter
from iambus.core import signals
from iambus.core.api.dispatcher import DispatcherProtocol
from iambus.core.api.typedef import UNHANDLED
from iambus.core.api.typing import MessageType

logger = getLogger('iambus.dispatcher')


class Dispatcher(DispatcherProtocol[EventRouter, RequestRouter]):
    """Base dispatcher protocol implementation."""
    _commands = None
    _queries = None

    def __init__(
        self,
        events_router_cls: type[EventRouter] = EventRouter,
        commands_router_cls: Optional[type[RequestRouter]] = None,
        queries_router_cls: Optional[type[RequestRouter]] = None,
        listen_for_signals: bool = True,
        engine_workers: int = 1,
    ) -> None:

        self._engine_workers = engine_workers
        self._routers = []

        if events_router_cls:
            self._events = events_router_cls(self)
            self._routers.append(self._events)

        if commands_router_cls:
            self._commands = commands_router_cls(self)
            self._routers.append(self._commands)

        if queries_router_cls:
            self._queries = queries_router_cls(self)
            self._routers.append(self._queries)

        self._listen_for_signals = listen_for_signals
        self._started = False

    @property
    def events(self):  # pragma: no cover
        if self._events is None:
            logger.info('attaching default event router')
            self._events = EventRouter(self)
            self._routers.append(self._events)

        return self._events

    @property
    def commands(self):  # pragma: no cover
        if self._commands is None:
            logger.info('attaching default command router')
            self._commands = RequestRouter(self)
            self._routers.append(self._commands)

        return self._commands

    @property
    def queries(self):  # pragma: no cover
        if self._queries is None:
            logger.info('attaching default query router')
            self._queries = RequestRouter(self)
            self._routers.append(self._queries)

        return self._queries

    def start(self) -> None:
        """Start the dispatcher."""

        if not any([
            self.events is not None,
            self.queries is not None,
            self.commands is not None
        ]):
            return logger.warning('no handlers registered')

        if self._events is not None:
            self.events.setup(workers=self._engine_workers)

        if self._commands is not None:
            self.commands.setup(workers=self._engine_workers)

        if self._queries is not None:
            self.queries.setup(workers=self._engine_workers)

        if self._listen_for_signals:
            signals.setup()

        logger.debug(f'{self.__class__.__name__} started.')
        self._started = True

    async def handle(
        self,
        message: MessageType,
        key: t.Optional[t.AnyStr] = None,
        wait_for_response: bool = False,
    ):
        """Try to handle message by event, command and query routers respectively.

        :param message: The message to handle.
        :param key: The key to use for the message partition.
        :param wait_for_response: If True, wait for a response.
        """
        for router in self._routers:
            response = await router.handle(
                message=message,
                key=key,
                wait_for_response=wait_for_response,
            )
            if response is not UNHANDLED:
                if inspect.isawaitable(response):
                    return await response
                return response

        logger.error(f'{message} was not handled.')


default_dispatcher = Dispatcher()
