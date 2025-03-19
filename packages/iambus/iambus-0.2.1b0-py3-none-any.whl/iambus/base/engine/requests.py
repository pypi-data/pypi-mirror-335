import typing as t

from iambus.base.engine.events import EventEngine
from iambus.base.maps import RequestHandlerMap
from iambus.core.api.engine import AbstractEngine
from iambus.core.api.typedef import RequestObject
from iambus.core.api.typing import MessageType, WrappedHandler


class RequestEngine(AbstractEngine[RequestHandlerMap]):

    def __init__(self, event_engine: EventEngine, message_map: RequestHandlerMap):
        super().__init__(message_map=message_map)
        self._event_engine = event_engine

    async def handle(
        self,
        handler: WrappedHandler,
        /,
        message: MessageType,
        key: t.Optional[t.AnyStr] = None,
    ):
        return await self.handle_one(handler, message, key)

    async def handle_side_events(
        self,
        handler: WrappedHandler,
        key: t.Optional[t.AnyStr] = None,
    ) -> None:
        """Handle side handler events"""
        for event in await handler.dump_events():
            await self._event_engine.put_to_queue(
                RequestObject(message=event, key=key, wait_for_response=False),
            )
