from iambus.base.engine.requests import RequestEngine
from iambus.base.maps import RequestHandlerMap
from iambus.base.routers.messagerouter import AbstractBaseMessageRouter


class RequestRouter(AbstractBaseMessageRouter[RequestEngine]):
    map_cls = RequestHandlerMap
    engine_cls = RequestEngine

    def get_engine(self):
        return self.engine_cls(event_engine=self._dispatcher.events.engine, message_map=self._map)
