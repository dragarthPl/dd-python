from __future__ import annotations

from functools import cmp_to_key
from typing import Callable

from attrs import frozen
from domaindrivers.smartschedule.planning.parallelization.parallel_stages import ParallelStages


@frozen
class ParallelStagesList:
    all: list[ParallelStages]

    @classmethod
    def empty(cls) -> "ParallelStagesList":
        return cls([])

    @classmethod
    def of(cls, *stages: ParallelStages) -> "ParallelStagesList":
        return cls(list(stages))

    def print(self) -> str:
        return " | ".join(map(lambda stages: stages.print(), self.all))

    def add(self, new_parallel_stages: ParallelStages) -> "ParallelStagesList":
        result: list[ParallelStages] = self.all + [new_parallel_stages]
        return ParallelStagesList(result)

    def all_sorted_with(self, comparing: Callable[[ParallelStages, ParallelStages], int]) -> list[ParallelStages]:
        return sorted(self.all, key=cmp_to_key(comparing))

    def all_sorted(self) -> list[ParallelStages]:
        return self.all_sorted_with(
            lambda parallel_stages_a, parallel_stages_b: (parallel_stages_a.print() > parallel_stages_b.print())
            - (parallel_stages_a.print() < parallel_stages_b.print())
        )
