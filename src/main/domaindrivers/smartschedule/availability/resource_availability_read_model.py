from datetime import datetime
from uuid import UUID

from domaindrivers.smartschedule.availability.calendar import Calendar
from domaindrivers.smartschedule.availability.calendars import Calendars
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from sqlalchemy import text, TextClause
from sqlalchemy.orm import Session


class ResourceAvailabilityReadModel:
    CALENDAR_QUERY: TextClause = text(
        """
            WITH AvailabilityWithLag AS (
                SELECT
                    resource_id,
                    taken_by,
                    from_date,
                    to_date,
                    COALESCE(LAG(to_date) OVER (PARTITION BY resource_id, taken_by ORDER BY from_date), from_date) AS prev_to_date
                FROM
                    availabilities
                WHERE
                    from_date >= :from_date
                    AND to_date <= :to_date
                    AND resource_id = ANY (:resource_id)

            ),
            GroupedAvailability AS (
                SELECT
                    resource_id,
                    taken_by,
                    from_date,
                    to_date,
                    prev_to_date,
                    CASE WHEN
                        from_date = prev_to_date
                        THEN 0 ELSE 1 END
                    AS new_group_flag,
                    SUM(CASE WHEN
                        from_date = prev_to_date
                        THEN 0 ELSE 1 END)
                    OVER (PARTITION BY resource_id, taken_by ORDER BY from_date) AS grp
                FROM
                    AvailabilityWithLag
            )
            SELECT
                resource_id,
                taken_by,
                MIN(from_date) AS start_date,
                MAX(to_date) AS end_date
            FROM
                GroupedAvailability
            GROUP BY
                resource_id, taken_by, grp
            ORDER BY
                start_date;
        """
    )

    __session: Session

    def __init__(self, session: Session) -> None:
        self.__session = session

    def load(self, resource_id: ResourceId, time_slot: TimeSlot) -> Calendar:
        loaded: Calendars = self.load_all({resource_id}, time_slot)
        return loaded.get(resource_id)

    def load_all(self, resource_ids: set[ResourceId], time_slot: TimeSlot) -> Calendars:
        ids: list[UUID] = list(map(lambda resource_id: resource_id.get_id(), resource_ids))
        results = self.__session.execute(
            self.CALENDAR_QUERY,
            {
                "from_date": time_slot.since,
                "to_date": time_slot.to,
                "resource_id": ids,
            },
        )

        calendars: dict[ResourceId, dict[Owner, list[TimeSlot]]] = {}

        for row in results.mappings().all():
            resource: UUID = row.get("resource_id")
            key: ResourceId = ResourceId(resource)
            taken_by_uuid: UUID = row.get("taken_by")
            taken_by: Owner = Owner(taken_by_uuid) if taken_by_uuid else Owner.none()
            from_date: datetime = row.get("start_date")
            to_date: datetime = row.get("end_date")
            loaded_slot: TimeSlot = TimeSlot(from_date, to_date)
            calendars.setdefault(key, {})
            calendars[key].setdefault(taken_by, []).append(loaded_slot)

        return Calendars.of(*[Calendar(key, value) for key, value in calendars.items()])
