import uuid
from datetime import datetime
from uuid import UUID

from attr import frozen
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId


@frozen
class CapabilitiesAllocated:
    event_id: UUID
    allocated_capability_id: UUID
    project_id: ProjectAllocationsId
    missing_demands: Demands
    occurred_at: datetime

    @classmethod
    def of(
        cls,
        allocated_capability_id: UUID,
        project_id: ProjectAllocationsId,
        missing_demands: Demands,
        occurred_at: datetime,
    ) -> "CapabilitiesAllocated":
        return cls(uuid.uuid4(), allocated_capability_id, project_id, missing_demands, occurred_at)
