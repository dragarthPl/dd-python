from datetime import timedelta
from functools import reduce

from domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.parallelization.stage_parallelization import StageParallelization
from domaindrivers.utils.duration import ZERO
from domaindrivers.utils.functional import Function


class DurationCalculator(Function[list[Stage], timedelta]):
    def apply(self, stages: list[Stage]) -> timedelta:
        parallelized_stages: ParallelStagesList = StageParallelization().of(set(stages))
        durations: dict[Stage, timedelta] = {identity: identity.duration for identity in stages}
        return reduce(
            lambda acc, duration: acc + duration,
            map(
                lambda parallel_stages: max(map(lambda stage: durations.get(stage, ZERO), parallel_stages.stages))
                or ZERO,
                parallelized_stages.all_sorted(),
            ),
            timedelta(days=0),
        )
