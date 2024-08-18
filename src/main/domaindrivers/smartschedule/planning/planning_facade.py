from datetime import datetime, timedelta

import injector
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.planning.demands import Demands
from domaindrivers.smartschedule.planning.demands_per_stage import DemandsPerStage
from domaindrivers.smartschedule.planning.parallelization.duration_calculator import DurationCalculator
from domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.parallelization.stage_parallelization import StageParallelization
from domaindrivers.smartschedule.planning.plan_chosen_resources import PlanChosenResources
from domaindrivers.smartschedule.planning.project import Project
from domaindrivers.smartschedule.planning.project_card import ProjectCard
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.planning.project_repository import ProjectRepository
from domaindrivers.smartschedule.planning.schedule.schedule import Schedule
from domaindrivers.smartschedule.shared.resource_name import ResourceName
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from sqlalchemy.orm import Session


@injector.inject
class PlanningFacade:
    __session: Session
    __project_repository: ProjectRepository
    __parallelization: StageParallelization
    __plan_chosen_resources_service: PlanChosenResources

    def __init__(
        self,
        session: Session,
        project_repository: ProjectRepository,
        parallelization: StageParallelization,
        resources_planning: PlanChosenResources,
    ) -> None:
        self.__session = session
        self.__project_repository = project_repository
        self.__parallelization = parallelization
        self.__plan_chosen_resources_service = resources_planning

    def add_new_project_with_stages(self, name: str, *stages: Stage) -> ProjectId:
        parallelized_stages: ParallelStagesList = self.__parallelization.of(set(stages))
        return self.add_new_project_with_parallel_stages(name, parallelized_stages)

    def add_new_project_with_parallel_stages(self, name: str, parallelized_stages: ParallelStagesList) -> ProjectId:
        project: Project = Project(name, parallelized_stages)
        self.__project_repository.save(project)
        return project.id

    # @Transactional
    def define_start_date(self, project_id: ProjectId, possible_start_date: datetime) -> None:
        with self.__session.begin_nested():
            project: Project = self.__project_repository.find_by_id(project_id).or_else_throw()
            project.add_schedule(possible_start_date)

    # @Transactional
    def define_project_stages(self, project_id: ProjectId, *stages: Stage) -> None:
        with self.__session.begin_nested():
            project: Project = self.__project_repository.find_by_id(project_id).or_else_throw()
            parallelized_stages: ParallelStagesList = self.__parallelization.of(set(stages))
            project.define_stages(parallelized_stages)

    # @Transactional
    def add_demands(self, project_id: ProjectId, demands: Demands) -> None:
        with self.__session.begin_nested():
            project: Project = self.__project_repository.find_by_id(project_id).or_else_throw()
            project.add_demands(demands)

    # @Transactional
    def define_demands_per_stage(self, project_id: ProjectId, demands_per_stage: DemandsPerStage) -> None:
        with self.__session.begin_nested():
            project: Project = self.__project_repository.find_by_id(project_id).or_else_throw()
            project.add_demands_per_stage(demands_per_stage)

    # @Transactional
    def define_resources_within_dates(
        self, project_id: ProjectId, chosen_resources: set[ResourceId], time_boundaries: TimeSlot
    ) -> None:
        with self.__session.begin_nested():
            self.__plan_chosen_resources_service.define_resources_within_dates(
                project_id, chosen_resources, time_boundaries
            )

    # @Transactional
    def adjust_stages_to_resource_availability(
        self, project_id: ProjectId, time_boundaries: TimeSlot, *stages: Stage
    ) -> None:
        with self.__session.begin_nested():
            self.__plan_chosen_resources_service.adjust_stages_to_resource_availability(
                project_id, time_boundaries, *stages
            )

    # @Transactional
    def plan_critical_stage_with_resource(
        self, project_id: ProjectId, critical_stage: Stage, critical_resource: ResourceName, stage_time_slot: TimeSlot
    ) -> None:
        with self.__session.begin_nested():
            project: Project = self.__project_repository.find_by_id(project_id).or_else_throw()
            project.add_schedule_stage(critical_stage, stage_time_slot)

    # @Transactional
    def plan_critical_stage(self, project_id: ProjectId, critical_stage: Stage, stage_time_slot: TimeSlot) -> None:
        with self.__session.begin_nested():
            project: Project = self.__project_repository.find_by_id(project_id).or_else_throw()
            project.add_schedule_stage(critical_stage, stage_time_slot)

    # @Transactional
    def define_manual_schedule(self, project_id: ProjectId, schedule: Schedule) -> None:
        with self.__session.begin_nested():
            project: Project = self.__project_repository.find_by_id(project_id).or_else_throw()
            project.add_schedule_direct(schedule)

    def duration_of(self, *stages: Stage) -> timedelta:
        return DurationCalculator().apply(list(stages))

    def load(self, project_id: ProjectId) -> ProjectCard:
        project: Project = self.__project_repository.find_by_id(project_id).or_else_throw()
        return self.__to_summary(project)

    def load_all(self, projects_ids: set[ProjectId]) -> list[ProjectCard]:
        return list(
            map(lambda project: self.__to_summary(project), self.__project_repository.find_all_by_id(projects_ids))
        )

    def __to_summary(self, project: Project) -> ProjectCard:
        return ProjectCard(
            project.id,
            project.name,
            project.get_parallelized_stages(),
            project.get_all_demands(),
            project.get_schedule(),
            project.get_demands_per_stage(),
            project.get_chosen_resources(),
        )
