from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class EventObject:
    _source: Any

    def __init__(self, source: Any):
        if source is None:
            raise AttributeError("null source")

        self._source = source

    @property
    def source(self) -> Any:
        return self._source

    def to_string(self) -> str:
        return f"{str(self.__class__.__name__)}[source={self._source}]"

    def __str__(self) -> str:
        return self.to_string()


class ApplicationEvent(EventObject, ABC):
    __timestamp: int

    def __init__(self, source: Any) -> None:
        super().__init__(source)
        self.__timestamp = round(datetime.now().timestamp())

    @property
    def timestamp(self) -> int:
        return self.__timestamp


class ApplicationEventPublisher(ABC):
    def publish_event(self, event: ApplicationEvent) -> None:
        self.publish_event_object(event)

    @abstractmethod
    def publish_event_object(self, event: Any) -> None: ...
