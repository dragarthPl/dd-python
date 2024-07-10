from typing import cast, TYPE_CHECKING
from uuid import UUID

from attrs import frozen

if TYPE_CHECKING:
    from src.main.domaindrivers.smartschedule.optimization.capacity_dimension import CapacityDimension
else:
    from domaindrivers.smartschedule.optimization.capacity_dimension import CapacityDimension

from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class AvailableResourceCapability(CapacityDimension):
    resource_id: UUID
    capability: Capability
    time_slot: TimeSlot

    def performs(self, capability: Capability) -> bool:
        return cast(bool, self.capability == capability)
