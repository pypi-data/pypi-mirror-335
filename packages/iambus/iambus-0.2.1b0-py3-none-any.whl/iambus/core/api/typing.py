import inspect
import typing as t

if t.TYPE_CHECKING:
    from iambus.core.api.engine import AbstractEngine  # noqa
    from iambus.core.api.handlers import (  # noqa
        AbstractHandler,
        AbstractHandlerWrapper,
        HandlerMetaDataProtocol,
    )
    from iambus.core.api.maps import AbstractHandlerMap  # noqa
    from iambus.core.api.routers import AbstractMessageRouter  # noqa

Message: t.TypeAlias = type[t.Any] | t.Hashable
MessageType = t.TypeVar("MessageType", bound=Message)

TypeKey = t.TypeVar("TypeKey", type, str)


P = t.ParamSpec("P")
PyBusHandler = t.TypeVar("PyBusHandler", bound="AbstractHandler")
WrappedHandler = t.TypeVar("WrappedHandler", bound="AbstractHandlerWrapper")

PyBusHandlerMeta = t.TypeVar("PyBusHandlerMeta", bound="HandlerMetaDataProtocol")

ReturnType = t.TypeVar("ReturnType", t.Any, None)
HandlerReturnType: t.TypeAlias = t.Awaitable[ReturnType]

HandlerType: t.TypeAlias = t.Union[
    PyBusHandler,
    WrappedHandler,
    t.Callable[[], HandlerReturnType],
    t.Callable[[MessageType], HandlerReturnType],
    t.Callable[[MessageType, P.kwargs], HandlerReturnType],
]

MessageMapType = t.TypeVar("MessageMapType", bound="AbstractHandlerMap")
MapReturnType = t.TypeVar("MapReturnType", HandlerType, frozenset[HandlerType])

EngineType = t.TypeVar("EngineType", bound="AbstractEngine")

EventRouterType = t.TypeVar('EventRouterType', bound="AbstractMessageRouter")
RequestRouterType = t.TypeVar('RequestRouterType', bound="AbstractMessageRouter")

Callback: t.TypeAlias = t.Callable[[...], t.Awaitable[...]]


def make_key(message: MessageType) -> TypeKey:
    """Return message key"""
    m_type = message if inspect.isclass(message) else type(message)
    return m_type if not issubclass(m_type, str) else message
