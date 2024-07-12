from __future__ import annotations

from functools import cmp_to_key
from typing import Any, Callable

from attrs import frozen
from domaindrivers.smartschedule.planning.parallelization.parallel_stages import ParallelStages


@frozen
class ParallelStagesList:
    all: list[ParallelStages]

    @classmethod
    def empty(cls) -> "ParallelStagesList":
        return cls([])

    @classmethod
    def of(cls, *parallel_stages: ParallelStages) -> "ParallelStagesList":
        return cls(list(parallel_stages))

    def print(self) -> str:
        return " | ".join(map(lambda stages: stages.print(), self.all))

    def add(self, new_parallel_stages: ParallelStages) -> "ParallelStagesList":
        result: list[ParallelStages] = self.all + [new_parallel_stages]
        return ParallelStagesList(result)

    def all_sorted(self, comparing: Callable[[Any, Any], Any]) -> list[ParallelStages]:
        return sorted(self.all, key=cmp_to_key(comparing))
