from typing import cast

import injector
from domaindrivers.smartschedule.planning.project import Project
from domaindrivers.smartschedule.planning.project_repository import ProjectRepository
from domaindrivers.utils.optional import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .project_id import ProjectId


class ProjectRepositoryImpl(ProjectRepository):  # type: ignore
    @injector.inject
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, project: Project) -> None:
        self.session.add(project)
        self.session.commit()

    def find_by_id(self, project_id: ProjectId) -> Optional[Project]:
        return Optional(self.session.query(Project).filter_by(_project_id=project_id.id()).first())

    def find_all_by_id(self, ids: list[ProjectId]) -> list[Project]:
        return cast(
            list[Project],
            self.session.query(Project).where(or_(*[Project._id == project_id for project_id in ids])).all(),
        )

    def find_all(self) -> list[Project]:
        return cast(list[Project], self.session.query(Project).all())

    def delete(self, project: Project) -> None:
        self.session.delete(project)
        self.session.commit()
