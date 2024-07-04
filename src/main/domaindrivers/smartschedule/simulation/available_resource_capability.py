from uuid import UUID

from attrs import frozen
from domaindrivers.smartschedule.optimization.capacity_dimension import CapacityDimension
from domaindrivers.smartschedule.shared.time_slot import TimeSlot
from domaindrivers.smartschedule.simulation.capability import Capability


@frozen
class AvailableResourceCapability(CapacityDimension):
    resource_id: UUID
    capability: Capability
    time_slot: TimeSlot

    def performs(self, capability: Capability) -> bool:
        return self.capability == capability
