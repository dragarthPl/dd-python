from attr import frozen
from domaindrivers.smartschedule.availability.calendar import Calendar
from domaindrivers.smartschedule.shared.resource_name import ResourceName


@frozen
class Calendars:
    calendars: dict[ResourceName, Calendar]

    @classmethod
    def of(cls, *calendars: Calendar) -> "Calendars":
        collect: dict[ResourceName, Calendar] = {calendar.resource_id: calendar for calendar in calendars}
        return Calendars(collect)

    def get(self, resource_id: ResourceName) -> Calendar:
        return self.calendars.get(resource_id, Calendar.empty(resource_id))
