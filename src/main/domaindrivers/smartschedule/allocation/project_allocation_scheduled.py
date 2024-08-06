import uuid
from datetime import datetime
from uuid import UUID

from attr import frozen
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class ProjectAllocationScheduled:
    uuid: UUID
    project_id: ProjectAllocationsId
    from_to: TimeSlot
    occurred_at: datetime

    @classmethod
    def of(
        cls, project_id: ProjectAllocationsId, from_to: TimeSlot, occured_at: datetime
    ) -> "ProjectAllocationScheduled":
        return cls(uuid.uuid4(), project_id, from_to, occured_at)
