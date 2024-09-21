from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Callable

from domaindrivers.smartschedule.shared.event import Event
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher

EventHandler = Callable[[Event], Any]


class EventsSubscriber(ABC):
    @abstractmethod
    def subscribe(self, event_handler: EventHandler, *event_types: str) -> None: ...


class EventBus(EventsPublisher, EventsSubscriber):  # type: ignore
    pass


class InMemoryEventBus(EventBus):
    _all_handlers: dict[str, list[EventHandler]]

    def __init__(self) -> None:
        self._all_handlers = defaultdict(list)

    def publish(self, event: Event) -> None:
        event_handlers = self._all_handlers.get(event.__class__.__name__, [])
        for handler in event_handlers:
            handler(event)

    def subscribe(self, event_handler: EventHandler, *event_types: str) -> None:
        for event_type in event_types:
            self._all_handlers[event_type].append(event_handler)
