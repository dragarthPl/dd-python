from attr import frozen
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_resource_id import AllocatableResourceId
from domaindrivers.smartschedule.shared.capability_selector import CapabilitySelector
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class AllocatableCapabilitySummary:
    allocatable_capability_id: AllocatableCapabilityId
    allocatableResourceId: AllocatableResourceId
    capabilities: CapabilitySelector
    time_slot: TimeSlot
