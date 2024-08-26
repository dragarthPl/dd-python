from functools import reduce

from domaindrivers.smartschedule.resource.employees.employee import Employee
from domaindrivers.smartschedule.resource.employees.employee_id import EmployeeId
from domaindrivers.smartschedule.resource.employees.employee_summary import EmployeeSummary
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.storage.repository import Repository
from domaindrivers.utils.functional import Predicate


class EmployeeRepository(Repository[Employee, EmployeeId]):
    def find_summary(self, employee_id: EmployeeId) -> EmployeeSummary:
        employee: Employee = self.find_by_id(employee_id).or_else_throw()
        skills: set[Capability] = self.__filter_capabilities(
            employee.capabilities(), Predicate[Capability](lambda cap: cap.is_of_type("SKILL"))
        )
        permissions: set[Capability] = self.__filter_capabilities(
            employee.capabilities(), Predicate[Capability](lambda cap: cap.is_of_type("PERMISSION"))
        )
        return EmployeeSummary(
            employee_id, employee.name(), employee.last_name(), employee.seniority(), skills, permissions
        )

    def find_all_capabilities(self) -> list[Capability]:
        return reduce(lambda n, m: n + list(m.capabilities()), self.find_all(), [])

    def __filter_capabilities(self, capabilities: set[Capability], p: Predicate[Capability]) -> set[Capability]:
        return set(filter(p, capabilities))
