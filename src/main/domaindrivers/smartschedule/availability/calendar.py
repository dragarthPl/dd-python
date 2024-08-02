from attr import frozen
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.shared.resource_name import ResourceName
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class Calendar:
    resource_id: ResourceName
    calendar: dict[Owner, list[TimeSlot]]

    @classmethod
    def with_available_slots(cls, resource_id: ResourceName, *available_slots: TimeSlot) -> "Calendar":
        return cls(resource_id, {Owner.none(): list(available_slots)})

    @classmethod
    def empty(cls, resource_id: ResourceName) -> "Calendar":
        return cls(resource_id, {})

    def available_slots(self) -> list[TimeSlot]:
        return self.calendar.get(Owner.none(), [])
