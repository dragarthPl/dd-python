from attrs import frozen
from domaindrivers.smartschedule.planning.parallelization.stage import Stage


@frozen
class ParallelStages:
    stages: set[Stage]

    def print(self) -> str:
        return ", ".join(sorted(map(lambda stage: stage.name, self.stages)))
