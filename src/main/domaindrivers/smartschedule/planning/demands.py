from attr import frozen
from domaindrivers.smartschedule.planning.demand import Demand


@frozen
class Demands:
    all: list[Demand]

    @classmethod
    def none(cls) -> "Demands":
        return cls([])

    @classmethod
    def of(cls, *demands: Demand) -> "Demands":
        return cls(list(demands))

    def add(self, demands: "Demands") -> "Demands":
        return Demands(self.all + demands.all)
