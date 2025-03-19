import asyncio
import typing as t
from logging import getLogger

from iambus.base.maps import EventHandlerMap
from iambus.core.api.engine import AbstractEngine
from iambus.core.api.typedef import UNHANDLED
from iambus.core.api.typing import MessageType, WrappedHandler

logger = getLogger(__name__)


class EventEngine(AbstractEngine[EventHandlerMap]):

    async def handle(
        self,
        handlers: frozenset[WrappedHandler],
        /,
        message: MessageType,
        key: t.Optional[t.AnyStr] = None,
    ):
        if not handlers:
            return UNHANDLED

        await asyncio.gather(
            *(self.handle_one(handler, message, key) for handler in handlers),
        )
