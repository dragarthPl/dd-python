from typing import cast

import injector
from domaindrivers.smartschedule.allocation.project_allocations import ProjectAllocations
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.allocation.project_allocations_repository import ProjectAllocationsRepository
from domaindrivers.utils.optional import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session


class ProjectAllocationsRepositoryImpl(ProjectAllocationsRepository):  # type: ignore
    @injector.inject
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, project: ProjectAllocations) -> None:
        self.session.add(project)
        self.session.commit()

    def find_by_id(self, project_id: ProjectAllocationsId) -> Optional[ProjectAllocations]:
        return Optional(
            self.session.query(ProjectAllocations).filter_by(_project_allocations_id=project_id.id()).first()
        )

    def find_all_by_id(self, ids: list[ProjectAllocationsId]) -> list[ProjectAllocations]:
        return cast(
            list[ProjectAllocations],
            self.session.query(ProjectAllocations)
            .where(or_(*[ProjectAllocations._project_id == project_id for project_id in ids]))
            .all(),
        )

    def find_all(self) -> list[ProjectAllocations]:
        return cast(list[ProjectAllocations], self.session.query(ProjectAllocations).all())

    def delete(self, project: ProjectAllocations) -> None:
        self.session.delete(project)
        self.session.commit()
