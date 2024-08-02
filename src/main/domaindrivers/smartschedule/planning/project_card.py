from attr import frozen
from domaindrivers.smartschedule.planning.chosen_resources import ChosenResources
from domaindrivers.smartschedule.planning.demands import Demands
from domaindrivers.smartschedule.planning.demands_per_stage import DemandsPerStage
from domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.planning.schedule.schedule import Schedule


@frozen
class ProjectCard:
    project_id: ProjectId
    name: str
    parallelized_stages: ParallelStagesList
    demands: Demands
    schedule: Schedule
    demands_per_stage: DemandsPerStage
    needed_resources: ChosenResources

    @classmethod
    def of(
        cls,
        project_id: ProjectId,
        name: str,
        parallelized_stages: ParallelStagesList,
        demands: Demands,
    ) -> "ProjectCard":
        return cls(
            project_id=project_id,
            name=name,
            parallelized_stages=parallelized_stages,
            demands=demands,
            schedule=Schedule.none(),
            demands_per_stage=DemandsPerStage.empty(),
            needed_resources=ChosenResources.none(),
        )
