from typing import cast, Type

import injector
from domaindrivers.smartschedule.allocation.capabilityscheduling.capability_scheduler import CapabilityScheduler
from domaindrivers.smartschedule.resource.employees.employee_facade import EmployeeFacade
from domaindrivers.smartschedule.resource.employees.employee_repository import EmployeeRepository
from domaindrivers.smartschedule.resource.employees.employee_repository_sqlalchemy import EmployeeRepositorySqlalchemy
from domaindrivers.smartschedule.resource.employees.schedule_employee_capabilities import ScheduleEmployeeCapabilities
from injector import Module, provider, singleton


class EmployeeConfiguration(Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(cast(Type[EmployeeRepository], EmployeeRepository), to=EmployeeRepositorySqlalchemy)

    @singleton
    @provider
    def employee_facade(
        self, employee_repository: EmployeeRepository, capability_scheduler: CapabilityScheduler
    ) -> EmployeeFacade:
        return EmployeeFacade(
            employee_repository, ScheduleEmployeeCapabilities(employee_repository, capability_scheduler)
        )
