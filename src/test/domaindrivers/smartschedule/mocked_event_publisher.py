from typing import Any

from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher


class MockedEventPublisher(EventsPublisher):  # type: ignore
    def publish(self, event: Any) -> None:
        pass
