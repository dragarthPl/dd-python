import uuid
from datetime import datetime
from uuid import UUID

from attr import frozen
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.shared.published_event import PublishedEvent


@frozen
class NotSatisfiedDemands(PublishedEvent):
    uuid: UUID
    missing_demands: dict[ProjectAllocationsId, Demands]
    __occurred_at: datetime

    def occurred_at(self) -> datetime:
        return self.__occurred_at

    @classmethod
    def of(cls, missing_demands: dict[ProjectAllocationsId, Demands], occured_at: datetime) -> "NotSatisfiedDemands":
        return cls(uuid.uuid4(), missing_demands, occured_at)

    @classmethod
    def for_one_project(
        cls, project_id: ProjectAllocationsId, scheduled_demands: Demands, occurred_at: datetime
    ) -> "NotSatisfiedDemands":
        return cls(uuid.uuid4(), {project_id: scheduled_demands}, occurred_at)

    @classmethod
    def all_satisfied(cls, project_id: ProjectAllocationsId, occurred_at: datetime) -> "NotSatisfiedDemands":
        return cls(uuid.uuid4(), {project_id: Demands.none()}, occurred_at)
