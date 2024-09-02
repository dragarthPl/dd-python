from attr import define, field
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_resource_id import AllocatableResourceId
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@define(slots=False)
class AllocatableCapability:
    _allocatable_capability_id: AllocatableCapabilityId = field(factory=AllocatableCapabilityId.new_one)
    _capability: Capability = field(default=None)
    _allocatable_resource_id: AllocatableResourceId = field(default=None)
    _time_slot: TimeSlot = field(default=None)

    def id(self) -> AllocatableCapabilityId:
        return self._allocatable_capability_id

    def can_perform(self, capability: Capability) -> bool:
        return capability == self._capability

    def resource_id(self) -> AllocatableResourceId:
        return self._allocatable_resource_id

    def slot(self) -> TimeSlot:
        return self._time_slot

    def capability(self) -> Capability:
        return self._capability
