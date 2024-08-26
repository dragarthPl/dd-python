from attr import frozen
from domaindrivers.smartschedule.resource.employees.employee_id import EmployeeId
from domaindrivers.smartschedule.resource.employees.seniority import Seniority
from domaindrivers.smartschedule.shared.capability.capability import Capability


@frozen
class EmployeeSummary:
    id: EmployeeId
    name: str
    last_name: str
    seniority: Seniority
    skills: set[Capability]
    permissions: set[Capability]
