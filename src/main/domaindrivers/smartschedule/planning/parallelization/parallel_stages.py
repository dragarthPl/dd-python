from attrs import frozen

from src.main.domaindrivers.smartschedule.planning.parallelization.stage import Stage


@frozen
class ParallelStages:
    stages: set[Stage]

    def print(self) -> str:
        return ", ".join(sorted(map(lambda stage: stage.name, self.stages)))
