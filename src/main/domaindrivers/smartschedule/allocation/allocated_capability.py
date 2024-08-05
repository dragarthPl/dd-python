import hashlib
import uuid
from typing import Any
from uuid import UUID

from attr import frozen
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class AllocatedCapability:
    allocated_capability_id: UUID
    resource_id: UUID
    capability: Capability
    time_slot: TimeSlot

    @classmethod
    def of(cls, resource_id: UUID, capability: Capability, time_slot: TimeSlot) -> "AllocatedCapability":
        return cls(uuid.uuid4(), resource_id, capability, time_slot)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AllocatedCapability):
            return False
        return (
            self.resource_id == other.resource_id
            and self.capability == other.capability
            and self.time_slot == other.time_slot
        )

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.resource_id).encode("utf-8"))
        m.update(str(self.capability).encode("utf-8"))
        m.update(str(self.time_slot).encode("utf-8"))

        return int(m.hexdigest(), 16)
