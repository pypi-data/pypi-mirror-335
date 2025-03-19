import typing as t

from iambus.core.api.typing import (
    EventRouterType,
    RequestRouterType, MessageType,
)


@t.runtime_checkable
class DispatcherProtocol(t.Protocol[EventRouterType, RequestRouterType]):
    """DispatcherProtocol protocol."""

    @property
    def events(self) -> EventRouterType:
        """Return events proxy"""

    @property
    def commands(self) -> RequestRouterType:
        """Return commands proxy"""

    @property
    def queries(self) -> RequestRouterType:
        """Return queries proxy"""

    async def handle(
        self,
        message: MessageType,
        key: t.Optional[t.AnyStr],
        wait_for_response: bool,
    ) -> t.Awaitable[...]:
        """Handle a message"""
