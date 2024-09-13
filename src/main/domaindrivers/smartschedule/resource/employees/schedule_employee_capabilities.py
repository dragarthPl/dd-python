from typing import Final

from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.capability_scheduler import CapabilityScheduler
from domaindrivers.smartschedule.resource.employees.employee_allocation_policy import (
    CompositePolicy,
    DefaultPolicy,
    EmployeeAllocationPolicy,
    OneOfSkills,
    PermissionsInMultipleProjects,
)
from domaindrivers.smartschedule.resource.employees.employee_id import EmployeeId
from domaindrivers.smartschedule.resource.employees.employee_repository import EmployeeRepository
from domaindrivers.smartschedule.resource.employees.employee_summary import EmployeeSummary
from domaindrivers.smartschedule.resource.employees.seniority import Seniority
from domaindrivers.smartschedule.shared.capability_selector import CapabilitySelector
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class ScheduleEmployeeCapabilities:
    __employee_repository: Final[EmployeeRepository]
    __capability_scheduler: Final[CapabilityScheduler]

    def __init__(self, employee_repository: EmployeeRepository, capability_scheduler: CapabilityScheduler):
        self.__employee_repository = employee_repository
        self.__capability_scheduler = capability_scheduler

    def setup_employee_capabilities(
        self, employee_id: EmployeeId, time_slot: TimeSlot
    ) -> list[AllocatableCapabilityId]:
        summary: EmployeeSummary = self.__employee_repository.find_summary(employee_id)
        policy: EmployeeAllocationPolicy = self.__find_allocation_policy(summary)
        capabilities: list[CapabilitySelector] = policy.simultaneous_capabilities_of(summary)

        return self.__capability_scheduler.schedule_resource_capabilities_for_period(
            employee_id.to_allocatable_resource_id(), capabilities, time_slot
        )

    def __find_allocation_policy(self, employee: EmployeeSummary) -> EmployeeAllocationPolicy:
        if employee.seniority == Seniority.LEAD:
            return CompositePolicy([OneOfSkills(), PermissionsInMultipleProjects(3)])
        return DefaultPolicy()
