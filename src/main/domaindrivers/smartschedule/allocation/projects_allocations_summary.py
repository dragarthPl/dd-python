from attr import frozen
from domaindrivers.smartschedule.allocation.allocations import Allocations
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocations import ProjectAllocations
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class ProjectsAllocationsSummary:
    time_slots: dict[ProjectAllocationsId, TimeSlot]
    project_allocations: dict[ProjectAllocationsId, Allocations]
    demands: dict[ProjectAllocationsId, Demands]

    @classmethod
    def of(cls, all_project_allocations: list[ProjectAllocations]) -> "ProjectsAllocationsSummary":
        time_slots: dict[ProjectAllocationsId, TimeSlot] = {
            project_allocations.id: project_allocations.time_slot()
            for project_allocations in filter(
                lambda project_allocations: project_allocations.has_time_slot(), all_project_allocations
            )
        }
        allocations: dict[ProjectAllocationsId, Allocations] = {
            project_allocations.id: project_allocations.allocations() for project_allocations in all_project_allocations
        }
        demands: dict[ProjectAllocationsId, Demands] = {
            project_allocations.id: project_allocations.demands() for project_allocations in all_project_allocations
        }
        return cls(time_slots, allocations, demands)
