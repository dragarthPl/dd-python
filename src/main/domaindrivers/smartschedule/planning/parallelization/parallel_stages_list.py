from __future__ import annotations

from attrs import frozen

from src.main.domaindrivers.smartschedule.planning.parallelization.parallel_stages import ParallelStages


@frozen
class ParallelStagesList:
    all: list[ParallelStages]

    def print(self) -> str:
        return " | ".join(map(lambda stages: stages.print(), self.all))
