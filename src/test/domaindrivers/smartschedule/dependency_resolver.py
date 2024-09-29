from typing import Callable, cast, Type, TypeVar

import injector
from domaindrivers.smartschedule.allocation.allocation_configuration import AllocationConfiguration
from domaindrivers.smartschedule.allocation.capabilityscheduling.capability_planning_configuration import (
    CapabilityPlanningConfiguration,
)
from domaindrivers.smartschedule.allocation.cashflow.cash_flow_configuration import CashFlowConfiguration
from domaindrivers.smartschedule.availability.availability_configuration import AvailabilityConfiguration
from domaindrivers.smartschedule.planning.planning_configuration import PlanningConfiguration
from domaindrivers.smartschedule.resource.device.device_configuration import DeviceConfiguration
from domaindrivers.smartschedule.resource.employees.employee_configuration import EmployeeConfiguration
from domaindrivers.smartschedule.resource.resource_configuration import ResourceConfiguration
from domaindrivers.smartschedule.risk.risk_configuration import RiskConfiguration
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher
from domaindrivers.storage.database import DatabaseModule
from domaindrivers.utils.events_publisher_in_memory import EventBus, InMemoryEventBus
from injector import Binder, Injector
from testcontainers.postgres import PostgresContainer

T = TypeVar("T")
postgres_container = PostgresContainer("postgres:16")


class DependencyResolverForTest:
    injector: Injector
    __in_memory_event_bus: InMemoryEventBus

    def __init__(self, database_uri: str, additional_configure: Callable[[Binder], None] = lambda _: None) -> None:
        self.__in_memory_event_bus = InMemoryEventBus()

        def configure(binder: Binder) -> None:
            binder.bind(
                cast(Type[EventsPublisher], EventsPublisher),
                to=self.__in_memory_event_bus,
                scope=injector.singleton,
            )
            binder.bind(cast(Type[EventBus], EventBus), to=self.__in_memory_event_bus, scope=injector.singleton)

        self.injector = Injector(
            [
                configure,
                DatabaseModule(database_uri=database_uri),
                PlanningConfiguration(),
                AllocationConfiguration(),
                CashFlowConfiguration(),
                AvailabilityConfiguration(),
                DeviceConfiguration(),
                EmployeeConfiguration(),
                ResourceConfiguration(),
                CapabilityPlanningConfiguration(),
                RiskConfiguration(),
                additional_configure,
            ]
        )

    def get_injector(self) -> Injector:
        return self.injector

    def resolve_dependency(self, interface: Type[T]) -> T:
        return self.injector.get(interface)
