from datetime import datetime
from typing import Sequence

import injector
from domaindrivers.smartschedule.allocation.project_allocations import ProjectAllocations
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.allocation.project_allocations_repository import ProjectAllocationsRepository
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.storage.repository import Repository
from domaindrivers.utils.optional import Optional
from sqlalchemy import column, or_, RowMapping, text
from sqlalchemy.orm import Session


class ProjectAllocationsRepositorySqlalchemy(
    ProjectAllocationsRepository, Repository[ProjectAllocations, ProjectAllocationsId]
):
    @injector.inject
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, project_id: ProjectAllocationsId) -> ProjectAllocations:
        return self.session.query(ProjectAllocations).filter_by(_project_allocations_id=project_id.id()).first()

    def save(self, project: ProjectAllocations) -> None:
        self.session.add(project)

    def find_by_id(self, project_id: ProjectAllocationsId) -> Optional[ProjectAllocations]:
        return Optional(
            self.session.query(ProjectAllocations).filter_by(_project_allocations_id=project_id.id()).first()
        )

    def find_all_by_id(self, ids: set[ProjectAllocationsId]) -> list[ProjectAllocations]:
        return (
            self.session.query(ProjectAllocations)
            .where(or_(*[column("project_allocations_id") == project_id.id() for project_id in ids]))
            .all()
        )

    def find_all(self) -> list[ProjectAllocations]:
        return self.session.query(ProjectAllocations).all()

    def delete(self, project: ProjectAllocations) -> None:
        self.session.delete(project)
        self.session.commit()

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
