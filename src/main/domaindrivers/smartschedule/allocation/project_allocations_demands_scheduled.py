import uuid
from datetime import datetime
from uuid import UUID

from attr import frozen
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId


@frozen
class ProjectAllocationsDemandsScheduled:
    uuid: UUID
    project_id: ProjectAllocationsId
    missing_demands: Demands
    occurred_at: datetime

    @classmethod
    def of(
        cls, project_id: ProjectAllocationsId, missing_demands: Demands, occured_at: datetime
    ) -> "ProjectAllocationsDemandsScheduled":
        return cls(uuid.uuid4(), project_id, missing_demands, occured_at)
