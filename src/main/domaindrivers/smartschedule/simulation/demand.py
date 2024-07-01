from attr import frozen
from domaindrivers.smartschedule.simulation.available_resource_capability import AvailableResourceCapability
from domaindrivers.smartschedule.simulation.capability import Capability
from domaindrivers.smartschedule.simulation.time_slot import TimeSlot


@frozen
class Demand:
    capability: Capability
    slot: TimeSlot

    @classmethod
    def demand_for(cls, capability: Capability, slot: TimeSlot) -> "Demand":
        return cls(capability, slot)

    def is_satisfied_by(self, available_capability: AvailableResourceCapability) -> bool:
        return bool(
            self.capability == available_capability.capability and self.slot.within(available_capability.time_slot)
        )
