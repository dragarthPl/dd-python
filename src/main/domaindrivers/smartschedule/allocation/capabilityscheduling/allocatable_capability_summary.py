from attr import frozen
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_resource_id import AllocatableResourceId
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class AllocatableCapabilitySummary:
    allocatable_capability_id: AllocatableCapabilityId
    allocatableResourceId: AllocatableResourceId
    capability: Capability
    time_slot: TimeSlot
