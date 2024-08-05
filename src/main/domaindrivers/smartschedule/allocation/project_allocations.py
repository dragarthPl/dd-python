from datetime import datetime
from uuid import UUID

from domaindrivers.smartschedule.allocation.allocations import Allocations
from domaindrivers.smartschedule.allocation.capabilities_allocated import CapabilitiesAllocated
from domaindrivers.smartschedule.allocation.capability_released import CapabilityReleased
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.allocation.resource_id import ResourceId
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.utils.optional import Optional


class ProjectAllocations:
    _project_id: ProjectAllocationsId
    _allocations: Allocations
    _demands: Demands
    _time_slot: TimeSlot

    def __init__(
        self,
        project_id: ProjectAllocationsId = None,
        allocations: Allocations = None,
        scheduled_demands: Demands = None,
        time_slot: TimeSlot = None,
    ) -> None:
        if project_id:
            self._project_id = project_id
        if allocations:
            self._allocations = allocations
        if scheduled_demands:
            self._demands = scheduled_demands
        if time_slot:
            self._time_slot = time_slot
        else:
            self._time_slot = None

    @classmethod
    def empty(cls, project_id: ProjectAllocationsId) -> "ProjectAllocations":
        return cls(project_id, Allocations.none(), Demands.none(), TimeSlot.empty())

    @classmethod
    def with_demands(cls, project_id: ProjectAllocationsId, demands: Demands) -> "ProjectAllocations":
        return cls(project_id, Allocations.none(), demands)

    def allocate(
        self, resource_id: ResourceId, capability: Capability, requested_slot: TimeSlot, when: datetime
    ) -> Optional[CapabilitiesAllocated]:
        if self.__nothing_allocated() or not self.__within_project_time_slot(requested_slot):
            return Optional.empty()
        return Optional.of(CapabilitiesAllocated(None, None, None, None, None))

    def __nothing_allocated(self) -> bool:
        return False

    def __within_project_time_slot(self, requested_slot: TimeSlot) -> bool:
        return False

    def release(
        self, allocated_capability_id: UUID, time_slot: TimeSlot, when: datetime
    ) -> Optional[CapabilityReleased]:
        if self.__nothing_released():
            return Optional.empty()
        return Optional.of(CapabilityReleased.of(None, None, None))

    def __nothing_released(self) -> bool:
        return False

    def missing_demands(self) -> Demands:
        return self._demands.missing_demands(self._allocations)

    def allocations(self) -> Allocations:
        return self._allocations

    def has_time_slot(self) -> bool:
        return self._time_slot is not None and not self._time_slot == TimeSlot.empty()
