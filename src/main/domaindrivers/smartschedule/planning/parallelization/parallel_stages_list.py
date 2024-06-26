from __future__ import annotations

from attrs import frozen
from domaindrivers.smartschedule.planning.parallelization.parallel_stages import ParallelStages


@frozen
class ParallelStagesList:
    all: list[ParallelStages]

    @classmethod
    def empty(cls) -> "ParallelStagesList":
        return cls([])

    def print(self) -> str:
        return " | ".join(map(lambda stages: stages.print(), self.all))

    def add(self, new_parallel_stages: ParallelStages) -> "ParallelStagesList":
        result: list[ParallelStages] = self.all + [new_parallel_stages]
        return ParallelStagesList(result)
