from attr import frozen
from domaindrivers.smartschedule.allocation.allocations import Allocations
from domaindrivers.smartschedule.allocation.demand import Demand


@frozen
class Demands:
    all: list[Demand]

    def missing_demands(self, allocations: Allocations) -> "Demands":
        return Demands(list(filter(lambda d: not self.satisfied_by(d, allocations), self.all)))

    def satisfied_by(self, d: Demand, allocations: Allocations) -> bool:
        return any([ar.capability == d.capability and d.slot.within(ar.time_slot) for ar in allocations.all])
