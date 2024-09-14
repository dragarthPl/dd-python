from typing import Final

from domaindrivers.smartschedule.allocation.allocation_facade import AllocationFacade
from domaindrivers.smartschedule.planning.project import Project
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.planning.project_repository import ProjectRepository
from domaindrivers.smartschedule.planning.schedule.schedule import Schedule
from sqlalchemy.orm import Session


class CreateProjectAllocations:
    __session: Session
    __allocation_facade: Final[AllocationFacade]
    __project_repository: Final[ProjectRepository]

    def __init__(
        self, session: Session, allocation_facade: AllocationFacade, project_repository: ProjectRepository
    ) -> None:
        self.__session = session
        self.__allocation_facade = allocation_facade
        self.__project_repository = project_repository

    # can react to ScheduleCalculated event
    # @Transactional
    def create_project_allocations(self, project_id: ProjectId) -> None:
        with self.__session.begin_nested():
            project: Project = self.__project_repository.find_by_id(project_id).or_else_throw()
            schedule: Schedule = project.get_schedule()  # noqa: F841
            # for each stage in schedule
            # create allocation
            # allocate chosen resources (or find equivalents)
            # start risk analysis
