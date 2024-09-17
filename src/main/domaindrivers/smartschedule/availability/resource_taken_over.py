import uuid
from datetime import datetime
from uuid import UUID

from attr import frozen
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.shared.event import Event
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class ResourceTakenOver(Event):
    event_id: UUID
    resource_id: ResourceId
    previous_owners: set[Owner]
    slot: TimeSlot
    __occurred_at: datetime

    def occurred_at(self) -> datetime:
        return self.__occurred_at

    @classmethod
    def of(
        cls, resource_id: ResourceId, previous_owners: set[Owner], slot: TimeSlot, occured_at: datetime
    ) -> "ResourceTakenOver":
        return cls(uuid.uuid4(), resource_id, previous_owners, slot, occured_at)
