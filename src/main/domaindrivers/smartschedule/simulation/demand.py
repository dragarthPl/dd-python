from typing import override

from attr import frozen
from domaindrivers.smartschedule.optimization.weight_dimension import WeightDimension
from domaindrivers.smartschedule.shared.time_slot import TimeSlot
from domaindrivers.smartschedule.simulation.available_resource_capability import AvailableResourceCapability
from domaindrivers.smartschedule.simulation.capability import Capability


@frozen
class Demand(WeightDimension[AvailableResourceCapability]):
    capability: Capability
    slot: TimeSlot

    @classmethod
    def demand_for(cls, capability: Capability, slot: TimeSlot) -> "Demand":
        return cls(capability, slot)

    @override
    def is_satisfied_by(self, available_capability: AvailableResourceCapability) -> bool:
        return bool(
            self.capability == available_capability.capability and self.slot.within(available_capability.time_slot)
        )
