from typing import cast

import injector
from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.planning.parallelization.stage_parallelization import StageParallelization
from domaindrivers.smartschedule.planning.plan_chosen_resources import PlanChosenResources
from domaindrivers.smartschedule.planning.planning_facade import PlanningFacade
from domaindrivers.smartschedule.planning.project_repository import ProjectRepository
from domaindrivers.smartschedule.planning.redis_project_repository import RedisProjectRepository
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher
from injector import Module, provider, singleton
from sqlalchemy.orm import Session


class PlanningConfiguration(Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(cast(type[ProjectRepository], ProjectRepository), to=RedisProjectRepository)

    @singleton
    @provider
    def planning_facade(
        self,
        session: Session,
        project_repository: ProjectRepository,
        plan_chosen_resources_service: PlanChosenResources,
        events_publisher: EventsPublisher,
    ) -> PlanningFacade:
        return PlanningFacade(
            session, project_repository, StageParallelization(), plan_chosen_resources_service, events_publisher
        )

    @singleton
    @provider
    def plan_chosen_resources_service(
        self,
        session: Session,
        project_repository: ProjectRepository,
        availability_facade: AvailabilityFacade,
        events_publisher: EventsPublisher,
    ) -> PlanChosenResources:
        return PlanChosenResources(session, project_repository, availability_facade, events_publisher)
