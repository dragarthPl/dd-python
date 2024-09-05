from typing import cast

from attr import define
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_resource_id import AllocatableResourceId
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.capability_selector import CapabilitySelector
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@define(slots=False)
class AllocatableCapability:
    _allocatable_capability_id: AllocatableCapabilityId = AllocatableCapabilityId.new_one()

    # @Type(JsonType.class)
    # @Column(columnDefinition = "jsonb")
    _possible_capabilities: CapabilitySelector = None

    # @Embedded
    _allocatable_resource_id: AllocatableResourceId = None

    # @Embedded
    # @AttributeOverrides({
    #         @AttributeOverride(name = "from", column = @Column(name = "from_date")),
    #         @AttributeOverride(name = "to", column = @Column(name = "to_date"))
    # })
    _time_slot: TimeSlot = None

    def __init__(
        self,
        allocatable_capability_id: AllocatableCapabilityId = None,
        allocatable_resource_id: AllocatableResourceId = None,
        possible_capabilities: CapabilitySelector = None,
        time_slot: TimeSlot = None,
    ) -> None:
        self._allocatable_capability_id = allocatable_capability_id or AllocatableCapabilityId.new_one()
        self._allocatable_resource_id = allocatable_resource_id
        self._possible_capabilities = possible_capabilities
        self._time_slot = time_slot

    def id(self) -> AllocatableCapabilityId:
        return self._allocatable_capability_id

    def can_perform(self, capabilities: set[Capability]) -> bool:
        return cast(bool, self.capabilities().can_perform_capabilities(capabilities))

    def resource_id(self) -> AllocatableResourceId:
        return self._allocatable_resource_id

    def slot(self) -> TimeSlot:
        return self._time_slot

    def capabilities(self) -> CapabilitySelector:
        return self._possible_capabilities
