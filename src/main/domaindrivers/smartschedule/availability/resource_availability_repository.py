from typing import Any
from uuid import UUID

import injector
from domaindrivers.smartschedule.availability.blockade import Blockade
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_availability import ResourceAvailability
from domaindrivers.smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from domaindrivers.smartschedule.availability.resource_grouped_availability import ResourceGroupedAvailability
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from sqlalchemy import Result, RowMapping, text
from sqlalchemy.orm import Session
from typing_extensions import Sequence


class ResourceAvailabilityRepository:
    __session: Session

    @injector.inject
    def __init__(self, session: Session):
        self.__session = session

    def session(self) -> Session:
        return self.__session

    def save_new_resource_availability(self, resource_availability: ResourceAvailability) -> None:
        self.__save_new_list_resource_availability([resource_availability])

    def save_new_resource_grouped_availability(self, grouped_availability: ResourceGroupedAvailability) -> None:
        self.__save_new_list_resource_availability(grouped_availability.availabilities())

    def __save_new_list_resource_availability(self, availabilities: list[ResourceAvailability]) -> None:
        statement = text(
            """
            INSERT INTO  availabilities
            (id, resource_id, resource_parent_id, from_date, to_date, taken_by, disabled, version)
            VALUES
            (:id, :resource_id, :resource_parent_id, :from_date, :to_date, :taken_by, :disabled, :version)
        """
        )
        self.__session.execute(
            statement,
            [
                {
                    "id": availability.id().resource_availability_id,
                    "resource_id": availability.resource_id().get_id(),
                    "resource_parent_id": availability.resource_parent_id().get_id(),
                    "from_date": availability.segment().since,
                    "to_date": availability.segment().to,
                    "taken_by": None,
                    "disabled": False,
                    "version": 0,
                }
                for availability in availabilities
            ],
        )

    def load_all_within_slot(self, resource_id: ResourceId, segment: TimeSlot) -> list[ResourceAvailability]:
        statement = text(
            """
            select * from availabilities where resource_id = :resource_id
                                and from_date >= :from_date and to_date <= :to_date
        """
        )
        result = self.__session.execute(
            statement,
            {
                "resource_id": resource_id.get_id(),
                "from_date": segment.since,
                "to_date": segment.to,
            },
        )
        return ResourceAvailabilityRowMapper.row_mapper(result.mappings().all())

    def load_all_by_parent_id_within_slot(self, parent_id: ResourceId, segment: TimeSlot) -> list[ResourceAvailability]:
        statement = text(
            """
            select * from availabilities where resource_parent_id = :resource_parent_id
                        and from_date >= :from_date and to_date <= :to_date
        """
        )
        result = self.__session.execute(
            statement,
            {
                "resource_parent_id": parent_id.get_id(),
                "from_date": segment.since,
                "to_date": segment.to,
            },
        )
        self.__session.commit()
        return ResourceAvailabilityRowMapper.row_mapper(result.mappings().all())

    def save_checking_version(self, resource_availability: ResourceAvailability) -> bool:
        resource_availability_id: UUID = resource_availability.id().resource_availability_id
        version: int = resource_availability.version()
        statement = text(
            """
           UPDATE availabilities
           SET taken_by = :taken_by, disabled = :disabled, version = :new_version
           WHERE id = :id AND version = :version
        """
        )
        update: Result[Any] = self.__session.execute(
            statement,
            {
                "taken_by": resource_availability.blocked_by().id(),
                "disabled": resource_availability.is_disabled(),
                "new_version": version + 1,
                "id": resource_availability_id,
                "version": version,
            },
        )
        return update.rowcount == 1  # type: ignore

    def save_checking_version_by_resource_grouped_availability(
        self, grouped_availability: ResourceGroupedAvailability
    ) -> bool:
        return self.save_checking_version_by_list(grouped_availability.availabilities())

    def save_checking_version_by_list(self, resource_availabilities: list[ResourceAvailability]) -> bool:
        statement = text(
            """
           UPDATE availabilities
           SET taken_by = :taken_by, disabled = :disabled, version = :new_version
           WHERE id = :id AND version = :version
        """
        )
        update_availabilities_list = [
            {
                "taken_by": ra.blocked_by().id(),
                "disabled": ra.is_disabled(),
                "new_version": ra.version() + 1,
                "id": ra.id().resource_availability_id,
                "version": ra.version(),
            }
            for ra in resource_availabilities
        ]
        if not update_availabilities_list:
            return True

        updates = self.__session.execute(
            statement,
            update_availabilities_list,
        )
        return bool(updates.rowcount == len(resource_availabilities))  # type: ignore

    def load_by_id(self, availability_id: ResourceAvailabilityId) -> ResourceAvailability:
        statement = text(
            """
            select * from availabilities where id = :id
        """
        )
        result = self.__session.execute(
            statement,
            {
                "id": availability_id.resource_availability_id,
            },
        )
        # self.__session.commit()
        return ResourceAvailabilityRowMapper.single_row_mapper(result.mappings().one())

    def load_availabilities_of_random_resource_within(
        self, resource_ids: set[ResourceAvailabilityId], normalized: TimeSlot
    ) -> ResourceGroupedAvailability:
        ids: list[UUID] = list(
            map(lambda resource_availability_id: resource_availability_id.resource_availability_id, resource_ids)
        )
        statement = text(
            """
         WITH AvailableResources AS (
            SELECT resource_id
            FROM availabilities
            WHERE resource_id = ANY(:ids)
            AND taken_by IS NULL
            AND from_date >= :from_date
            AND to_date <= :to_date
            GROUP BY resource_id
          ),
          RandomResource AS (
            SELECT resource_id
            FROM AvailableResources
            ORDER BY RANDOM()
            LIMIT 1
          )
          SELECT a.*
          FROM availabilities a
          JOIN RandomResource r ON a.resource_id = r.resource_id
        """
        )

        result = self.__session.execute(
            statement,
            {
                "ids": ids,
                "from_date": normalized.since,
                "to_date": normalized.to,
            },
        )
        availabilities: list[ResourceAvailability] = ResourceAvailabilityRowMapper.row_mapper(result.mappings().all())
        return ResourceGroupedAvailability(availabilities)


class ResourceAvailabilityRowMapper:
    @staticmethod
    def single_row_mapper(row: RowMapping) -> ResourceAvailability:
        resource_availability_id: ResourceAvailabilityId = ResourceAvailabilityId.of(row.get("id"))
        resource_id: ResourceId = ResourceId.of(row.get("resource_id"))
        segment: TimeSlot = TimeSlot(row.get("from_date"), row.get("to_date"))
        parent_id: ResourceId = ResourceId.of(row.get("resource_parent_id"))
        is_disabled: bool = row.get("disabled")
        result: Owner = None
        owner_id: UUID = row.get("taken_by")
        if not owner_id:
            result = Owner.none()
        else:
            result = Owner(owner_id)
        blocade: Blockade = Blockade(result, is_disabled)
        version: int = row.get("version")
        return ResourceAvailability(resource_availability_id, resource_id, segment, parent_id, blocade, version)

    @classmethod
    def row_mapper(cls, rows: Sequence[RowMapping]) -> list[ResourceAvailability]:
        return [cls.single_row_mapper(row) for row in rows]
