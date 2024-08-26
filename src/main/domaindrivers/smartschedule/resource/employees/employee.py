from attr import define, field
from domaindrivers.smartschedule.resource.employees.employee_id import EmployeeId
from domaindrivers.smartschedule.resource.employees.seniority import Seniority
from domaindrivers.smartschedule.shared.capability.capability import Capability


@define(slots=False)
class Employee:
    _id: EmployeeId = field(factory=EmployeeId.new_one)
    _name: str = field(default=None)
    _last_name: str = field(default=None)
    _seniority: Seniority = field(default=None)

    _capabilities: set[Capability] = field(factory=set)
    _version: int = field(default=0)

    def name(self) -> str:
        return self._name

    def last_name(self) -> str:
        return self._last_name

    def seniority(self) -> Seniority:
        return self._seniority

    def capabilities(self) -> set[Capability]:
        return self._capabilities

    def id(self) -> EmployeeId:
        return self._id
