from datetime import datetime

from attr import define
from domaindrivers.smartschedule.allocation.demand import Demand
from domaindrivers.smartschedule.planning.chosen_resources import ChosenResources
from domaindrivers.smartschedule.planning.demands import Demands
from domaindrivers.smartschedule.planning.demands_per_stage import DemandsPerStage
from domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.planning.schedule.schedule import Schedule
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@define(slots=False)
class Project:
    # @EmbeddedId
    _id: ProjectId

    # @Version
    _version: int

    _name: str

    # @Type(JsonType.class)
    # @Column(columnDefinition = "jsonb")
    _parallelized_stages: ParallelStagesList

    # @Type(JsonType.class)
    # @Column(columnDefinition = "jsonb")
    _demands_per_stage: DemandsPerStage

    # @Type(JsonType.class)
    # @Column(columnDefinition = "jsonb")
    _all_demands: Demands

    # @Type(JsonType.class)
    # @Column(columnDefinition = "jsonb")
    _chosen_resources: ChosenResources

    # @Type(JsonType.class)
    # @Column(columnDefinition = "jsonb")
    _schedule: Schedule

    def __init__(
        self,
        name: str,
        parallelized_stages: ParallelStagesList,
        demands_per_stage: DemandsPerStage = None,
        all_demands: Demands = None,
        schedule: Schedule = None,
        chosen_resources: ChosenResources = None,
        version: int = 0,
        project_id: ProjectId = None,
    ):
        self._name = name
        self._parallelized_stages = parallelized_stages
        self._schedule = Schedule.none()  # Placeholder for Schedule.none()
        self._demands_per_stage = demands_per_stage or DemandsPerStage.empty()
        self._all_demands = all_demands or Demands.none()
        self._schedule = schedule or Schedule.none()
        self._chosen_resources = chosen_resources or ChosenResources.none()
        self._version = version
        self._id = project_id or ProjectId.new_one()

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
