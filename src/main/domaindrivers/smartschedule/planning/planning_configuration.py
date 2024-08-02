from typing import cast, Type

import injector
from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.planning.parallelization.stage_parallelization import StageParallelization
from domaindrivers.smartschedule.planning.plan_chosen_resources import PlanChosenResources
from domaindrivers.smartschedule.planning.planning_facade import PlanningFacade
from domaindrivers.smartschedule.planning.project_repository import ProjectRepository
from domaindrivers.smartschedule.planning.project_repository_sqlalchemy import ProjectRepositorySqlalchemy
from injector import Module, provider, singleton
from sqlalchemy.orm import Session


class PlanningConfiguration(Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(cast(Type[ProjectRepository], ProjectRepository), to=ProjectRepositorySqlalchemy)

    @singleton
    @provider
    def planning_facade(
        self,
        session: Session,
        project_repository: ProjectRepository,
        plan_chosen_resources_service: PlanChosenResources,
    ) -> PlanningFacade:
        return PlanningFacade(session, project_repository, StageParallelization(), plan_chosen_resources_service)

    @singleton
    @provider
    def plan_chosen_resources_service(
        self, session: Session, project_repository: ProjectRepository
    ) -> PlanChosenResources:
        return PlanChosenResources(session, project_repository, AvailabilityFacade())
