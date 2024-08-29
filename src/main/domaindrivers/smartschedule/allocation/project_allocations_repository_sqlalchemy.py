import injector
from domaindrivers.smartschedule.allocation.project_allocations import ProjectAllocations
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.allocation.project_allocations_repository import ProjectAllocationsRepository
from domaindrivers.utils.optional import Optional
from sqlalchemy import column, or_
from sqlalchemy.orm import Session


class ProjectAllocationsRepositorySqlalchemy(ProjectAllocationsRepository):
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
