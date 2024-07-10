from uuid import UUID

from attr import frozen
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class AllocatedCapability:
    resource_id: UUID
    capability: Capability
    time_slot: TimeSlot
