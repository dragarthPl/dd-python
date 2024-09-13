from abc import ABC, abstractmethod

from domaindrivers.smartschedule.resource.employees.employee_summary import EmployeeSummary
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.capability_selector import CapabilitySelector


class EmployeeAllocationPolicy(ABC):
    @abstractmethod
    def simultaneous_capabilities_of(self, employee: EmployeeSummary) -> list[CapabilitySelector]: ...


class DefaultPolicy(EmployeeAllocationPolicy):
    def simultaneous_capabilities_of(self, employee: EmployeeSummary) -> list[CapabilitySelector]:
        all_capability: set[Capability] = set()
        all_capability = all_capability.union(employee.skills)
        all_capability = all_capability.union(employee.permissions)
        return [CapabilitySelector.can_perform_one_of(all_capability)]


class PermissionsInMultipleProjects(EmployeeAllocationPolicy):
    __how_many: int

    def __init__(self, how_many: int):
        self.__how_many = how_many

    def simultaneous_capabilities_of(self, employee: EmployeeSummary) -> list[CapabilitySelector]:
        return [
            CapabilitySelector.can_just_perform(permission)
            for permission in employee.permissions
            for _ in range(self.__how_many)
        ]


class OneOfSkills(EmployeeAllocationPolicy):
    def simultaneous_capabilities_of(self, employee: EmployeeSummary) -> list[CapabilitySelector]:
        return [CapabilitySelector.can_perform_one_of(employee.skills)]


class CompositePolicy(EmployeeAllocationPolicy):
    def __init__(self, policies: list[EmployeeAllocationPolicy]):
        self.__policies = policies

    def simultaneous_capabilities_of(self, employee: EmployeeSummary) -> list[CapabilitySelector]:
        return [
            capability for policy in self.__policies for capability in policy.simultaneous_capabilities_of(employee)
        ]
