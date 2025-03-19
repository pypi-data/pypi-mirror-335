from typing import NamedTuple, Optional, TypeVar

from iambus.base.handlers.wrapper import HandlerWrapper
from iambus.core.api.maps import AbstractHandlerMap
from iambus.core.api.typing import (
    HandlerType,
    MapReturnType,
    MessageType,
    PyBusHandlerMeta, make_key,
)
from iambus.core.exceptions import HandlerDoesNotExist
from iambus.core.types import EMPTY

EmptySet = frozenset()
HandlerFrozenSet = TypeVar("HandlerFrozenSet", bound=frozenset[HandlerType])


class HandlerMetaData(NamedTuple):
    """Meta data for dispatcher"""
    inject: bool
    argname: Optional[str] = EMPTY
    message: Optional[MessageType] = EMPTY


class EventHandlerMap(AbstractHandlerMap[HandlerFrozenSet]):
    """Event handler map."""

    def add(self, message: MessageType, handler: HandlerType) -> None:
        if self._frozen:
            raise RuntimeError("map is frozen")

        self._storage.setdefault(make_key(message), set()).add(handler)

    def find(self, key: MessageType) -> MapReturnType:
        return self._storage.get(make_key(key), EmptySet)

    @classmethod
    def freeze(cls, val: set[HandlerType]) -> MapReturnType:
        return frozenset(val)

    def wrap_handler(self, meta: PyBusHandlerMeta) -> HandlerWrapper:
        wrapped = HandlerWrapper(meta=meta)
        self.add(message=meta.message, handler=wrapped)
        return wrapped


class RequestHandlerMap(AbstractHandlerMap[HandlerType]):
    """Request handler map."""

    def add(self, message: MessageType, handler: HandlerType) -> None:
        if self._frozen:
            raise RuntimeError("map is frozen")

        self._storage[make_key(message)] = handler

    def find(self, key: MessageType) -> MapReturnType:
        try:
            return self._storage[make_key(key)]
        except KeyError as exc:
            raise HandlerDoesNotExist(pymessage=key) from exc

    @classmethod
    def freeze(cls, val: HandlerType) -> MapReturnType:
        return val

    def wrap_handler(self, meta: PyBusHandlerMeta) -> HandlerWrapper:
        wrapped = HandlerWrapper(meta=meta)
        self.add(message=meta.message, handler=wrapped)
        return wrapped
