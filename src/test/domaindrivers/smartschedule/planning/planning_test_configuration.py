from typing import Final
from unittest.mock import MagicMock

from domaindrivers.smartschedule.planning.parallelization.stage_parallelization import StageParallelization
from domaindrivers.smartschedule.planning.plan_chosen_resources import PlanChosenResources
from domaindrivers.smartschedule.planning.planning_facade import PlanningFacade
from domaindrivers.smartschedule.planning.project import Project
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.planning.project_repository import ProjectRepository
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher
from domaindrivers.utils.optional import Optional
from mockito import mock


class InMemoryProjectRepository(ProjectRepository):
    __projects: Final[dict[ProjectId, Project]]

    def __init__(self) -> None:
        self.__projects = {}

    def find_by_id(self, project_id: ProjectId) -> Optional[Project]:
        return Optional.of(self.__projects.get(project_id, None))

    def save(self, project: Project) -> Project:
        self.__projects[project.id] = project
        return self.__projects[project.id]

    def find_all_by_id_in(self, project_ids: set[ProjectId]) -> list[Project]:
        return [value for key, value in self.__projects.items() if key in project_ids]

    def find_all(self) -> list[Project]:
        return list(self.__projects.values())


class PlanningTestConfiguration:
    @staticmethod
    def planning_facade(events_publisher: EventsPublisher, project_repository: ProjectRepository) -> PlanningFacade:
        plan_chosen_resources: PlanChosenResources = PlanChosenResources(
            MagicMock(), project_repository, mock(), events_publisher
        )
        return PlanningFacade(
            MagicMock(), project_repository, StageParallelization(), plan_chosen_resources, events_publisher
        )
