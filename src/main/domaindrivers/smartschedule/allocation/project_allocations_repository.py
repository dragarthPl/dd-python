from datetime import datetime
from typing import Sequence

from domaindrivers.smartschedule.allocation.project_allocations import ProjectAllocations
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.storage.repository import Repository
from sqlalchemy import RowMapping, text
from sqlalchemy.orm import Session


class ProjectAllocationsRepository(Repository[ProjectAllocations, ProjectAllocationsId]):
    session: Session

    def find_all_containing_date(self, when: datetime) -> list[ProjectAllocations]:
        statement = text("SELECT * FROM project_allocations WHERE from_date <= :when AND to_date > :when")
        result = self.session.execute(
            statement,
            {
                "when": when,
            },
        )
        return ProjectAllocationsRowMapper.row_mapper(result.mappings().all())


class ProjectAllocationsRowMapper:
    @staticmethod
    def single_row_mapper(row: RowMapping) -> ProjectAllocations:
        project_id = ProjectAllocationsId(row["project_allocations_id"])
        allocations = row["allocations"]
        scheduled_demands = row["demands"]
        time_slot = TimeSlot(row.get("from_date"), row.get("to_date"))
        return ProjectAllocations(
            project_id,
            allocations,
            scheduled_demands,
            time_slot,
        )

    @classmethod
    def row_mapper(cls, rows: Sequence[RowMapping]) -> list[ProjectAllocations]:
        return [cls.single_row_mapper(row) for row in rows]
