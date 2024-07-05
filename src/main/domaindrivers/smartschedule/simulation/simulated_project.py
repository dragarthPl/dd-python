import hashlib
from decimal import Decimal
from typing import Any, Callable

from attrs import frozen
from domaindrivers.smartschedule.simulation.demands import Demands
from domaindrivers.smartschedule.simulation.project_id import ProjectId


@frozen
class SimulatedProject:
    project_id: ProjectId
    __value: Callable[[], Decimal]
    missing_demands: Demands

    def calculate_value(self) -> Decimal:
        return self.__value()

    def __eq__(self, other: Any) -> bool:
        if other is None or not isinstance(other, SimulatedProject):
            return False
        return bool(
            self.project_id == other.project_id
            and self.calculate_value() == other.calculate_value()
            and self.missing_demands == other.missing_demands
        )

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.project_id).encode("utf-8"))
        m.update(str(self.__value()).encode("utf-8"))
        m.update(str(self.missing_demands).encode("utf-8"))

        return int(m.hexdigest(), 16)
