from abc import ABC, abstractmethod

from domaindrivers.smartschedule.shared.application_event import ApplicationEvent


class EventsPublisher(ABC):
    # remember about transactions scope
    @abstractmethod
    def publish(self, event: ApplicationEvent) -> None: ...
