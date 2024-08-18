from attr import frozen
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class Calendar:
    resource_id: ResourceId
    calendar: dict[Owner, list[TimeSlot]]

    @classmethod
    def with_available_slots(cls, resource_id: ResourceId, *available_slots: TimeSlot) -> "Calendar":
        return cls(resource_id, {Owner.none(): list(available_slots)})

    @classmethod
    def empty(cls, resource_id: ResourceId) -> "Calendar":
        return cls(resource_id, {})

    def available_slots(self) -> list[TimeSlot]:
        return self.calendar.get(Owner.none(), [])

    def taken_by(self, requester: Owner) -> list[TimeSlot]:
        return self.calendar.get(requester, [])
