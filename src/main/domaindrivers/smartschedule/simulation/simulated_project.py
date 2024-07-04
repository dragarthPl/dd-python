import hashlib
from decimal import Decimal
from typing import Any

from attrs import frozen
from domaindrivers.smartschedule.simulation.demands import Demands
from domaindrivers.smartschedule.simulation.project_id import ProjectId


@frozen
class SimulatedProject:
    project_id: ProjectId
    earnings: Decimal
    missing_demands: Demands

    def __eq__(self, other: Any) -> bool:
        if other is None or not isinstance(other, SimulatedProject):
            return False
        return bool(
            self.project_id == other.project_id
            and self.earnings == other.earnings
            and self.missing_demands == other.missing_demands
        )

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.project_id).encode("utf-8"))
        m.update(str(self.earnings).encode("utf-8"))
        m.update(str(self.missing_demands).encode("utf-8"))

        return int(m.hexdigest(), 16)
