import abc
import typing as t

from iambus.base.handlers.wrapper import HandlerWrapper
from iambus.core.api.routers import AbstractMessageRouter
from iambus.core.api.typing import EngineType, HandlerType, MessageType
from iambus.core.inspection import sig


class AbstractBaseMessageRouter(
    AbstractMessageRouter[EngineType, HandlerWrapper],
    t.Generic[EngineType],
    metaclass=abc.ABCMeta
):
    """Base class for event and request router implementations."""

    def get_meta(
        self,
        message: MessageType,
        handler: HandlerType,
        argname: t.Optional[str],
        response_event: t.Optional[MessageType],
        **initkwargs,
    ) -> sig.HandlerMetaData:
        """Return Handler meta"""
        return sig.check_signature(
            handler,
            message,
            argname,
            response_event,
            **initkwargs
        )
