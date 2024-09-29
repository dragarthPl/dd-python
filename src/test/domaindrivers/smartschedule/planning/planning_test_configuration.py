from test.domaindrivers.smartschedule.planning.planning_db_test_configuration import PlanningDbTestConfiguration
from typing import cast, Type, TypeVar

import injector
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher
from domaindrivers.utils.events_publisher_in_memory import EventBus, InMemoryEventBus
from injector import Injector, Module

T = TypeVar("T")


class PlanningTestConfiguration(Module):
    injector: Injector

    def __init__(self) -> None:
        self.__in_memory_event_bus = InMemoryEventBus()

        def configure(binder: injector.Binder) -> None:
            binder.bind(
                cast(Type[EventsPublisher], EventsPublisher), to=self.__in_memory_event_bus, scope=injector.singleton
            )
            binder.bind(cast(Type[EventBus], EventBus), to=self.__in_memory_event_bus, scope=injector.singleton)

        self.injector = Injector([configure, PlanningDbTestConfiguration()])

    def get_injector(self) -> Injector:
        return self.injector

    def resolve_dependency(self, interface: Type[T]) -> T:
        return self.injector.get(interface)
