import uuid
from datetime import datetime
from uuid import UUID

from attr import frozen
from domaindrivers.smartschedule.planning.demands import Demands
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.shared.event import Event


@frozen
class CapabilitiesDemanded(Event):
    uuid: UUID
    project_id: ProjectId
    demands: Demands
    __occurred_at: datetime

    def occurred_at(self) -> datetime:
        return self.__occurred_at

    @classmethod
    def of(cls, project_id: ProjectId, demands: Demands, occurred_at: datetime) -> "CapabilitiesDemanded":
        return cls(
            uuid.uuid4(),
            project_id,
            demands,
            occurred_at,
        )
