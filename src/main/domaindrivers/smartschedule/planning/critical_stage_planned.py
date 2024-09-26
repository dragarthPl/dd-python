from datetime import datetime

from attr import frozen
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.shared.published_event import PublishedEvent
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class CriticalStagePlanned(PublishedEvent):
    project_id: ProjectId
    stage_time_slot: TimeSlot
    critical_resource: ResourceId
    __occurred_at: datetime

    def occurred_at(self) -> datetime:
        return self.__occurred_at
