import hashlib
from typing import Any

from attr import field, frozen
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class AllocatedCapability:
    allocated_capability_id: AllocatableCapabilityId
    capability: Capability
    time_slot: TimeSlot = field(default=None)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AllocatedCapability):
            return False
        return self.capability == other.capability and self.time_slot == other.time_slot

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.capability).encode("utf-8"))
        m.update(str(self.time_slot).encode("utf-8"))

        return int(m.hexdigest(), 16)
