from typing import Type, TypeVar

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
from domaindrivers.storage.database import DatabaseModule
from injector import Injector
from testcontainers.postgres import PostgresContainer

T = TypeVar("T")
postgres_container = PostgresContainer("postgres:16")


class DependencyResolverForTest:
    injector: Injector

    def __init__(self, database_uri: str):
        def configure(binder: injector.Binder) -> None:
            pass

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
            ]
        )

    def resolve_dependency(self, interface: Type[T]) -> T:
        return self.injector.get(interface)
