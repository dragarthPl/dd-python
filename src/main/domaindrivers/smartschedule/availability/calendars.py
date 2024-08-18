from attr import frozen
from domaindrivers.smartschedule.availability.calendar import Calendar
from domaindrivers.smartschedule.availability.resource_id import ResourceId


@frozen
class Calendars:
    calendars: dict[ResourceId, Calendar]

    @classmethod
    def of(cls, *calendars: Calendar) -> "Calendars":
        collect: dict[ResourceId, Calendar] = {calendar.resource_id: calendar for calendar in calendars}
        return Calendars(collect)

    def get(self, resource_id: ResourceId) -> Calendar:
        return self.calendars.get(resource_id, Calendar.empty(resource_id))
