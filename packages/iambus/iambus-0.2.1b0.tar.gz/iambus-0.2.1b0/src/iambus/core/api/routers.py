import abc
import functools
import typing as t
from collections.abc import Callable
from typing import Optional, AnyStr

from iambus.core.api.dispatcher import DispatcherProtocol
from iambus.core.api.handlers import HandlerMetaDataProtocol
from iambus.core.api.maps import AbstractHandlerMap
from iambus.core.api.typedef import RequestObject, UNHANDLED
from iambus.core.api.typing import (
    EngineType,
    HandlerType,
    MessageType,
    WrappedHandler,
)
from iambus.core.types import EMPTY


class AbstractMessageRouter(
    t.Generic[EngineType, WrappedHandler],
    metaclass=abc.ABCMeta,
):
    """Router protocol."""
    map_cls: type[AbstractHandlerMap]
    engine_cls: type[EngineType]

    def __init__(self, dispatcher: DispatcherProtocol):
        self._dispatcher = dispatcher
        self._map = self.get_map()
        self._engine: Optional[EngineType] = None

    async def handle(
        self,
        message: MessageType,
        *,
        key: Optional[AnyStr] = None,
        wait_for_response: bool = False,
    ) -> t.Awaitable[...]:
        """Handle message with optional partition key."""
        assert self._engine.is_started, "you should start the engine first"

        if not self._map.can_handle(message):
            return UNHANDLED

        return await self._engine.put_to_queue(
            RequestObject(message=message, key=key, wait_for_response=wait_for_response)
        )

    @property
    def engine(self) -> EngineType:
        """Return the engine for this router."""
        return self._engine

    def get_map(self):
        """Returns the message handler map."""
        if self.map_cls is None:
            raise NotImplementedError()

        return self.map_cls()

    def bind(
        self,
        message: MessageType,
        handler: HandlerType,
        argname: t.Optional[str] = EMPTY,
        response_event: t.Optional[MessageType] = None,
        **initkwargs,
    ) -> WrappedHandler:
        """Bind handler for the given message."""
        meta = self.get_meta(
            message,
            handler,
            argname,
            response_event,
            **initkwargs
        )
        return self._map.wrap_handler(meta)

    def register(
        self,
        message: MessageType,
        argname: t.Optional[str] = EMPTY,
        response_event: t.Optional[MessageType] = None,
        **initkwargs,
    ) -> Callable:
        """Register handler for the given message as decorator."""

        def _wrapper(handler: HandlerType):
            wrapped_handler = self.bind(
                message,
                handler,
                argname,
                response_event,
                **initkwargs
            )

            @functools.wraps(handler)
            async def _decorated(*args, **kwargs):
                return await wrapped_handler.handle(*args, **kwargs)

            return _decorated

        return _wrapper

    @abc.abstractmethod
    def get_meta(
        self,
        message: MessageType,
        handler: HandlerType,
        argname: t.Optional[str],
        response_event: t.Optional[MessageType],
        **initkwargs,
    ) -> HandlerMetaDataProtocol:
        """Return Handler meta"""

    @abc.abstractmethod
    def get_engine(self):
        """Set up the engine for this router."""

    def setup(self, workers: int):
        """setup map, routes, ..."""
        self._map.build()
        self._engine = self.get_engine()
        self._engine.start(workers=workers)
