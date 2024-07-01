from attrs import field, frozen
from domaindrivers.smartschedule.simulation.demand import Demand


@frozen
class Demands:
    all: list[Demand] = field(factory=list)

    @classmethod
    def of(cls, *demands: Demand) -> "Demands":
        return cls(list(demands))
