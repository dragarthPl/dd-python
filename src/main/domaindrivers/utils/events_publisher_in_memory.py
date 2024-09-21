from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Callable

from domaindrivers.smartschedule.shared.application_event import ApplicationEvent
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher


class EventsSubscriber(ABC):
    @abstractmethod
    def subscribe(self, event_handler: Callable[[ApplicationEvent], None], *event_types: str) -> None: ...


class EventBus(EventsPublisher, EventsSubscriber, ABC):
    pass


class InMemoryEventBus(EventBus):
    _all_handlers: dict[str, list[Callable[[ApplicationEvent], None]]]

    def __init__(self) -> None:
        self._all_handlers = defaultdict(list)

    def publish(self, event: ApplicationEvent) -> None:
        event_handlers = self._all_handlers.get(event.__class__.__name__, [])
        for handler in event_handlers:
            handler(event)

    def subscribe(self, event_handler: Callable[[ApplicationEvent], None], *event_types: str) -> None:
        for event_type in event_types:
            self._all_handlers[event_type].append(event_handler)  # type: ignore
