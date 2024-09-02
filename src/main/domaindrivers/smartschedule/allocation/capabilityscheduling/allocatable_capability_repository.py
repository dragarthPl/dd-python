from datetime import datetime
from typing import Sequence

from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability import AllocatableCapability
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_resource_id import AllocatableResourceId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.storage.repository import Repository
from sqlalchemy import RowMapping, text
from sqlalchemy.orm import Session


class AllocatableCapabilityRepository(Repository[AllocatableCapability, AllocatableCapabilityId]):
    session: Session

    def find_by_capability_within(
        self, name: str, capability_type: str, since: datetime, to: datetime
    ) -> list[AllocatableCapability]:
        statement = text(
            "SELECT *"
            " FROM allocatable_capabilities"
            " WHERE capability #>> '{py/state,name}' = :name"
            " AND capability #>> '{py/state,type}' = :capability_type"
            " AND from_date <= :since"
            " AND to_date >= :to"
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

    def save_all(self, entities: list[AllocatableCapability]) -> None: ...


class AllocatableCapabilityRowMapper:
    @staticmethod
    def single_row_mapper(row: RowMapping) -> AllocatableCapability:
        allocatable_capability_id = AllocatableCapabilityId(row["id"])
        resource_id = AllocatableResourceId(row["resource_id"])
        capability = row["capability"]
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
