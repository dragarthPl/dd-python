import hashlib
from typing import Any
from uuid import UUID

from attrs import frozen
from domaindrivers.smartschedule.optimization.capacity_dimension import CapacityDimension
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.capability_selector import CapabilitySelector
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class AvailableResourceCapability(CapacityDimension):
    resource_id: UUID
    capability_selector: CapabilitySelector
    time_slot: TimeSlot

    @classmethod
    def from_capability(
        cls, resource_id: UUID, capability: Capability, time_slot: TimeSlot
    ) -> "AvailableResourceCapability":
        return cls(resource_id, CapabilitySelector.can_just_perform(capability), time_slot)

    def performs(self, capability: Capability) -> bool:
        return self.capability_selector.can_perform_capabilities({capability})

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AvailableResourceCapability):
            return False
        return (
            self.resource_id == other.resource_id
            and self.capability_selector == other.capability_selector
            and self.time_slot == other.time_slot
        )

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.resource_id).encode("utf-8"))
        m.update(str(self.capability_selector).encode("utf-8"))
        m.update(str(self.time_slot).encode("utf-8"))

        return int(m.hexdigest(), 16)
