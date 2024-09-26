import uuid
from datetime import datetime
from uuid import UUID

from attr import frozen
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.shared.private_event import PrivateEvent


@frozen
class CapabilityReleased(PrivateEvent):
    event_id: UUID
    project_id: ProjectAllocationsId
    missing_demands: Demands
    __occurred_at: datetime

    @classmethod
    def of(
        cls, project_id: ProjectAllocationsId, missing_demands: Demands, occured_at: datetime
    ) -> "CapabilityReleased":
        return cls(uuid.uuid4(), project_id, missing_demands, occured_at)

    def occurred_at(self) -> datetime:
        return self.__occurred_at
