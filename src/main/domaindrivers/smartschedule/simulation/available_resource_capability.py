from uuid import UUID

from attrs import frozen
from domaindrivers.smartschedule.simulation.capability import Capability
from domaindrivers.smartschedule.simulation.time_slot import TimeSlot


@frozen
class AvailableResourceCapability:
    resource_id: UUID
    capability: Capability
    time_slot: TimeSlot

    def performs(self, capability: Capability) -> bool:
        return self.capability == capability
