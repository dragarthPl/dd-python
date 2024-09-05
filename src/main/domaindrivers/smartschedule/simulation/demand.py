from typing import override

from attr import frozen
from domaindrivers.smartschedule.optimization.weight_dimension import WeightDimension
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.smartschedule.simulation.available_resource_capability import AvailableResourceCapability


@frozen
class Demand(WeightDimension[AvailableResourceCapability]):
    capability: Capability
    slot: TimeSlot

    @classmethod
    def demand_for(cls, capability: Capability, slot: TimeSlot) -> "Demand":
        return cls(capability, slot)

    @override
    def is_satisfied_by(self, available_capability: AvailableResourceCapability) -> bool:
        return bool(available_capability.performs(self.capability) and self.slot.within(available_capability.time_slot))
