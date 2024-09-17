from datetime import datetime

from attrs import define, field
from domaindrivers.smartschedule.allocation.allocated_capability import AllocatedCapability
from domaindrivers.smartschedule.allocation.allocations import Allocations
from domaindrivers.smartschedule.allocation.capabilities_allocated import CapabilitiesAllocated
from domaindrivers.smartschedule.allocation.capability_released import CapabilityReleased
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocation_scheduled import ProjectAllocationScheduled
from domaindrivers.smartschedule.allocation.project_allocations_demands_scheduled import (
    ProjectAllocationsDemandsScheduled,
)
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.shared.capability_selector import CapabilitySelector
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.utils.optional import Optional


@define(slots=False)
class ProjectAllocations:
    _project_id: ProjectAllocationsId = field(default=None)
    _allocations: Allocations = field(default=None)
    _demands: Demands = field(default=None)
    _time_slot: TimeSlot = field(default=None)

    @classmethod
    def empty(cls, project_id: ProjectAllocationsId) -> "ProjectAllocations":
        return cls(project_id, Allocations.none(), Demands.none(), TimeSlot.empty())

    @classmethod
    def with_demands(cls, project_id: ProjectAllocationsId, demands: Demands) -> "ProjectAllocations":
        return cls(project_id, Allocations.none(), demands)

    def allocate(
        self,
        allocatable_capability_id: AllocatableCapabilityId,
        capability: CapabilitySelector,
        requested_slot: TimeSlot,
        when: datetime,
    ) -> Optional[CapabilitiesAllocated]:
        allocated_capability: AllocatedCapability = AllocatedCapability(
            allocatable_capability_id, capability, requested_slot
        )
        new_allocations: Allocations = self._allocations.add(allocated_capability)
        if self.__nothing_allocated(new_allocations) or not self.__within_project_time_slot(requested_slot):
            return Optional.empty()
        self._allocations = new_allocations
        return Optional.of(
            CapabilitiesAllocated.of(
                allocated_capability.allocated_capability_id.get_id(), self._project_id, self.missing_demands(), when
            )
        )

    def __nothing_allocated(self, new_allocations: Allocations) -> bool:
        return new_allocations == self._allocations

    def __within_project_time_slot(self, requested_slot: TimeSlot) -> bool:
        if not self.has_time_slot():
            return True
        return requested_slot.within(self._time_slot)

    def release(
        self, allocated_capability_id: AllocatableCapabilityId, time_slot: TimeSlot, when: datetime
    ) -> Optional[CapabilityReleased]:
        new_allocations: Allocations = self._allocations.remove(allocated_capability_id, time_slot)
        if new_allocations == self._allocations:
            return Optional.empty()
        self._allocations = new_allocations
        return Optional.of(CapabilityReleased.of(self._project_id, self.missing_demands(), when))

    def __nothing_released(self) -> bool:
        return False

    def missing_demands(self) -> Demands:
        return self._demands.missing_demands(self._allocations)

    def demands(self) -> Demands:
        return self._demands

    def allocations(self) -> Allocations:
        return self._allocations

    def has_time_slot(self) -> bool:
        return self._time_slot is not None and not self._time_slot == TimeSlot.empty()

    def define_slot(self, time_slot: TimeSlot, when: datetime) -> Optional[ProjectAllocationScheduled]:
        self._time_slot = time_slot
        return Optional.of(ProjectAllocationScheduled.of(self._project_id, self._time_slot, when))

    def add_demands(self, new_demands: Demands, when: datetime) -> Optional[ProjectAllocationsDemandsScheduled]:
        self._demands = self._demands.with_new(new_demands)
        return Optional.of(ProjectAllocationsDemandsScheduled.of(self._project_id, self.missing_demands(), when))

    @property
    def id(self) -> ProjectAllocationsId:
        return self._project_id

    def time_slot(self) -> TimeSlot:
        return self._time_slot
