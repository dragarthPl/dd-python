from attr import define, field
from domaindrivers.smartschedule.resource.employees.employee_id import EmployeeId
from domaindrivers.smartschedule.resource.employees.seniority import Seniority
from domaindrivers.smartschedule.shared.capability.capability import Capability


@define(slots=False)
class Employee:
    _name: str
    _last_name: str
    _seniority: Seniority

    # @Type(JsonType.class)
    # @Column(columnDefinition = "jsonb")
    _capabilities: set[Capability]
    _version: int = 0

    _id: EmployeeId = field(factory=EmployeeId.new_one)

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

    def __init__(
        self,
        employee_id: EmployeeId = EmployeeId.new_one(),
        name: str = None,
        last_name: str = None,
        seniority: Seniority = None,
        capabilities: set[Capability] = None,
    ) -> None:
        self._id = employee_id
        self._name = name
        self._last_name = last_name
        self._seniority = seniority
        self._capabilities = capabilities
