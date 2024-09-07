from datetime import datetime
from typing import Sequence
from uuid import UUID

from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability import AllocatableCapability
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_resource_id import AllocatableResourceId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.storage.repository import Repository
from domaindrivers.utils.optional import Optional
from sqlalchemy import RowMapping, text
from sqlalchemy.orm import Session


class AllocatableCapabilityRepository(Repository[AllocatableCapability, AllocatableCapabilityId]):
    session: Session

    def find_by_capability_within(
        self, name: str, capability_type: str, since: datetime, to: datetime
    ) -> list[AllocatableCapability]:
        statement = text(
            "SELECT ac.*, o.obj"
            " FROM allocatable_capabilities ac"
            " CROSS JOIN LATERAL jsonb_array_elements(ac.possible_capabilities -> 'py/state' -> 'capabilities' -> 'py/set') AS o(obj)"
            " WHERE o.obj #>> '{py/state,name}' = :name AND o.obj #>> '{py/state,type}' = :capability_type AND "
            " ac.from_date <= :since and ac.to_date >= :to"
        )
        result = self.session.execute(
            statement,
            {
                "name": name,
                "capability_type": capability_type,
                "since": since,
                "to": to,
            },
        )

        return AllocatableCapabilityRowMapper.row_mapper(result.mappings().all())

    def find_by_resource_id_and_capability_and_time_slot(
        self, allocatable_resource_id: UUID, name: str, capability_type: str, since: datetime, to: datetime
    ) -> Optional[AllocatableCapability]:
        statement = text(
            "FROM allocatable_capabilities ac "
            " CROSS JOIN LATERAL jsonb_array_elements(ac.possible_capabilities -> 'py/state' -> 'capabilities' -> 'py/set') AS o(obj)"
            " WHERE ac.resource_id = :allocatable_resource_id AND o.obj #>> '{py/state,name}' = :name AND "
            " o.obj #>> '{py/state,type}' = :capability_type "
            " AND ac.from_date = :since and ac.to_date = :to"
        )
        result = self.session.execute(
            statement,
            {
                "allocatable_resource_id": allocatable_resource_id,
                "name": name,
                "capability_type": capability_type,
                "since": since,
                "to": to,
            },
        )

        return Optional(AllocatableCapabilityRowMapper.single_row_mapper(result.mappings().first()))

    def find_by_resource_id_and_time_slot(
        self, allocatable_resource_id: UUID, since: datetime, to: datetime
    ) -> list[AllocatableCapability]:
        statement = text(
            "FROM allocatable_capabilities ac "
            "WHERE ac.resource_id = :allocatable_resource_id AND ac.from_date = :since and ac.to_date = :to"
        )
        result = self.session.execute(
            statement,
            {
                "allocatable_resource_id": allocatable_resource_id,
                "since": since,
                "to": to,
            },
        )
        return AllocatableCapabilityRowMapper.row_mapper(result.mappings().all())

    def save_all(self, entities: list[AllocatableCapability]) -> None: ...

    def exists_by_id(self, allocatable_capability_id: AllocatableCapabilityId) -> bool: ...


class AllocatableCapabilityRowMapper:
    @staticmethod
    def single_row_mapper(row: RowMapping) -> AllocatableCapability:
        allocatable_capability_id = AllocatableCapabilityId(row["id"])
        resource_id = AllocatableResourceId(row["resource_id"])
        capability = row["possible_capabilities"]
        time_slot = TimeSlot(row.get("from_date"), row.get("to_date"))
        return AllocatableCapability(
            allocatable_capability_id,
            capability,
            resource_id,
            time_slot,
        )

    @classmethod
    def row_mapper(cls, rows: Sequence[RowMapping]) -> list[AllocatableCapability]:
        return [cls.single_row_mapper(row) for row in rows]
