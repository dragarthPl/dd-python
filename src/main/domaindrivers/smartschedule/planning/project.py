from datetime import datetime

from attr import define
from attrs import field
from domaindrivers.smartschedule.planning.chosen_resources import ChosenResources
from domaindrivers.smartschedule.planning.demand import Demand
from domaindrivers.smartschedule.planning.demands import Demands
from domaindrivers.smartschedule.planning.demands_per_stage import DemandsPerStage
from domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.planning.schedule.schedule import Schedule
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@define(slots=False)
class Project:
    _name: str = field(default=None)
    _parallelized_stages: ParallelStagesList = field(default=None)

    _demands_per_stage: DemandsPerStage = field(factory=DemandsPerStage.empty)
    _all_demands: Demands = field(factory=Demands.none)
    _schedule: Schedule = field(factory=Schedule.none)
    _chosen_resources: ChosenResources = field(factory=ChosenResources.none)
    _version: int = field(default=0)
    _id: ProjectId = field(factory=ProjectId.new_one)

    @property
    def id(self) -> ProjectId:
        return self._id

    @property
    def project_id(self) -> ProjectId:
        return self._id

    @project_id.setter
    def project_id(self, project_id: ProjectId) -> None:
        self._id = project_id

    @property
    def name(self) -> str:
        return self._name

    def add_demands(self, demands: Demands) -> None:
        self._all_demands = self._all_demands.add(demands)

    def get_all_demands(self) -> Demands:
        return self._all_demands

    def get_parallelized_stages(self) -> ParallelStagesList:
        return self._parallelized_stages

    def add_schedule(self, possible_start_date: datetime) -> None:
        self._schedule = Schedule.based_on_start_day(possible_start_date, self._parallelized_stages)

    def add_chosen_resources(self, needed_resources: ChosenResources) -> None:
        self._chosen_resources = needed_resources

    def get_chosen_resources(self) -> ChosenResources:
        return self._chosen_resources

    def add_demands_per_stage(self, demands_per_stage: DemandsPerStage) -> None:
        self._demands_per_stage = demands_per_stage
        unique_demands: set[Demand] = {
            demand for demands in demands_per_stage.demands.values() for demand in demands.all
        }
        self.add_demands(Demands(list(unique_demands)))

    def get_demands_per_stage(self) -> DemandsPerStage:
        return self._demands_per_stage

    def add_schedule_stage(self, critical_stage: Stage, stage_time_slot: TimeSlot) -> None:
        self._schedule = Schedule.based_on_reference_stage_time_slot(
            critical_stage, stage_time_slot, self._parallelized_stages
        )

    def add_schedule_direct(self, schedule: Schedule) -> None:
        self._schedule = schedule

    def get_schedule(self) -> Schedule:
        return self._schedule

    def define_stages(self, parallelized_stages: ParallelStagesList) -> None:
        self._parallelized_stages = parallelized_stages

    def get_name(self) -> str:
        return self._name

    def get_id(self) -> ProjectId:
        return self._id
