import injector
from domaindrivers.smartschedule.shared.application_event_publisher import ApplicationEventPublisher
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher
from injector import Module, provider, singleton


class EventingConfiguration(Module):
    def configure(self, binder: injector.Binder) -> None:
        pass

    @singleton
    @provider
    def events_publisher(self, application_event_publisher: ApplicationEventPublisher) -> EventsPublisher:
        return None
