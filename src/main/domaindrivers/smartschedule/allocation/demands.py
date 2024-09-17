from attr import frozen
from domaindrivers.smartschedule.allocation.allocations import Allocations
from domaindrivers.smartschedule.allocation.demand import Demand
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class Demands:
    all: list[Demand]

    @classmethod
    def none(self) -> "Demands":
        return Demands([])

    @classmethod
    def of(cls, *demands: Demand) -> "Demands":
        return cls(list(demands))

    @classmethod
    def all_in_same_time_slot(cls, slot: TimeSlot, *capabilities: Capability) -> "Demands":
        return cls(list(map(lambda c: Demand(c, slot), capabilities)))

    def missing_demands(self, allocations: Allocations) -> "Demands":
        return Demands(list(filter(lambda d: not self.satisfied_by(d, allocations), self.all)))

    def satisfied_by(self, d: Demand, allocations: Allocations) -> bool:
        return any([ar.capability.can_perform(d.capability) and d.slot.within(ar.time_slot) for ar in allocations.all])

    def with_new(self, new_demands: "Demands") -> "Demands":
        all: list[Demand] = self.all.copy()
        all.extend(new_demands.all.copy())
        return Demands(all)
