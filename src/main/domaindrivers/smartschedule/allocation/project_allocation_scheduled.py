import uuid
from datetime import datetime
from uuid import UUID

from attr import frozen
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.shared.private_event import PrivateEvent
from domaindrivers.smartschedule.shared.published_event import PublishedEvent
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class ProjectAllocationScheduled(PublishedEvent, PrivateEvent):
    uuid: UUID

    project_id: ProjectAllocationsId
    from_to: TimeSlot
    __occurred_at: datetime

    def occurred_at(self) -> datetime:
        return self.__occurred_at

    @classmethod
    def of(
        cls, project_id: ProjectAllocationsId, from_to: TimeSlot, occurred_at: datetime
    ) -> "ProjectAllocationScheduled":
        return cls(uuid.uuid4(), project_id, from_to, occurred_at)
