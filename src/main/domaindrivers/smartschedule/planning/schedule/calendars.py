from typing import List
from uuid import UUID

from attr import frozen
from domaindrivers.smartschedule.planning.parallelization.resource_name import ResourceName
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class Owner:
    owner: UUID

    @classmethod
    def none(cls) -> "Owner":
        return Owner(None)


@frozen
class Calendar:
    resource_id: ResourceName
    calendar: dict[Owner, List[TimeSlot]]

    @classmethod
    def with_available_slots(cls, resource_id: ResourceName, *available_slots: TimeSlot) -> "Calendar":
        return cls(resource_id, {Owner.none(): list(available_slots)})

    @classmethod
    def empty(cls, resource_id: ResourceName) -> "Calendar":
        return cls(resource_id, {})

    def available_slots(self) -> List[TimeSlot]:
        return self.calendar.get(Owner.none(), [])


@frozen
class Calendars:
    calendars: dict[ResourceName, Calendar]

    @classmethod
    def of(cls, *calendars: Calendar) -> "Calendars":
        collect: dict[ResourceName, Calendar] = {calendar.resource_id: calendar for calendar in calendars}
        return Calendars(collect)

    def get(self, resource_id: ResourceName) -> Calendar:
        return self.calendars.get(resource_id, Calendar.empty(resource_id))
