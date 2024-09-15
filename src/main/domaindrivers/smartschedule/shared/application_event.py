from typing import TypeVar

from domaindrivers.smartschedule.shared.event import Event

ApplicationEvent = TypeVar("ApplicationEvent", bound=Event)
