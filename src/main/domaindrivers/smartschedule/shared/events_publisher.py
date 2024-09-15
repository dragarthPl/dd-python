from abc import ABC, abstractmethod

from domaindrivers.smartschedule.shared.event import Event


class EventsPublisher(ABC):
    # remember about transactions scope
    @abstractmethod
    def publish(self, event: Event) -> None: ...
