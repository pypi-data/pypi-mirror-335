import asyncio
import typing as t
from dataclasses import dataclass, field

from iambus.core.api.isolation import IsolationKey
from iambus.core.api.typing import MessageType, make_key

UNHANDLED = object()


def _future_cb() -> asyncio.Future:
    loop = asyncio.get_event_loop()
    return loop.create_future()


@dataclass(kw_only=True, slots=True)
class RequestObject:
    """Represents a request object."""
    message: MessageType
    key: t.Optional[t.AnyStr] = None
    wait_for_response: bool = False
    callback: asyncio.Future = field(default_factory=_future_cb)

    def isolation_key(self):
        """Isolation key of the request object."""
        return IsolationKey(obj_key=self.key, event_key=make_key(self.message))


@dataclass
class ResponseObject:
    """Represents a response object."""
    pass
