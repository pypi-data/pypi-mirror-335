import asyncio
import contextlib
from collections import defaultdict
from dataclasses import dataclass
from typing import AnyStr, Optional

from iambus.core.api.typing import TypeKey


@dataclass(frozen=True, slots=True, kw_only=True)
class IsolationKey:
    """Event identify key"""
    event_key: TypeKey
    """Event key: type of the message or value if message is string"""
    obj_key: Optional[AnyStr] = None
    """Optional key for the partition message"""


class IsolationManager:
    """Lock manager for events"""
    __slots__ = ("_locks",)

    def __init__(self):
        self._locks: dict[IsolationKey, asyncio.Lock] = defaultdict(asyncio.Lock)

    @contextlib.asynccontextmanager
    async def get_lock(self, ikey: IsolationKey):
        """Acquire lock in context"""
        async with self._locks[ikey]:
            yield
