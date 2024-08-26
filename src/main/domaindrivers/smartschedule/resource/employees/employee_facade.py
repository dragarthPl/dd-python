from typing import Final

from domaindrivers.smartschedule.resource.employees.employee import Employee
from domaindrivers.smartschedule.resource.employees.employee_id import EmployeeId
from domaindrivers.smartschedule.resource.employees.employee_repository import EmployeeRepository
from domaindrivers.smartschedule.resource.employees.employee_summary import EmployeeSummary
from domaindrivers.smartschedule.resource.employees.seniority import Seniority
from domaindrivers.smartschedule.shared.capability.capability import Capability


class EmployeeFacade:
    __employee_repository: Final[EmployeeRepository]

    def __init__(self, employee_repository: EmployeeRepository):
        self.__employee_repository = employee_repository

    def find_employee(self, employee_id: EmployeeId) -> EmployeeSummary:
        return self.__employee_repository.find_summary(employee_id)

    def find_all_capabilities(self) -> list[Capability]:
        return self.__employee_repository.find_all_capabilities()

    def add_employee(
        self, name: str, last_name: str, seniority: Seniority, skills: set[Capability], permissions: set[Capability]
    ) -> EmployeeId:
        employee_id: EmployeeId = EmployeeId.new_one()
        capabilities: set[Capability] = skills.union(permissions)
        employee: Employee = Employee(employee_id, name, last_name, seniority, capabilities)
        return self.__employee_repository.save(employee).id()

    # add vacation
    #  calls availability
    # add sick leave
    #  calls availability
    # change skills
