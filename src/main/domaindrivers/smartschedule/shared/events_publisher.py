from abc import ABC, abstractmethod

from domaindrivers.smartschedule.shared.published_event import PublishedEvent


class EventsPublisher(ABC):
    # remember about transactions scope
    @abstractmethod
    def publish(self, event: PublishedEvent) -> None: ...
