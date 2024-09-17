from datetime import datetime

from attr import frozen
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.shared.event import Event
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class NeededResourcesChosen(Event):
    project_id: ProjectId
    needed_resources: set[ResourceId]
    time_slot: TimeSlot
    __occurred_at: datetime

    def occurred_at(self) -> datetime:
        return self.__occurred_at
