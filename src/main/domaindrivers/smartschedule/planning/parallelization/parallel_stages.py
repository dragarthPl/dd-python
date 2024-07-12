from datetime import timedelta

from attrs import frozen
from domaindrivers.smartschedule.planning.parallelization.stage import Stage


@frozen
class ParallelStages:
    stages: set[Stage]

    def print(self) -> str:
        return ", ".join(sorted(map(lambda stage: stage.name, self.stages)))

    @classmethod
    def of(cls, *stages: Stage) -> "ParallelStages":
        return ParallelStages(set(stages))

    def duration(self) -> timedelta:
        return max(map(lambda stage: stage.duration, self.stages)) or timedelta(seconds=0)
