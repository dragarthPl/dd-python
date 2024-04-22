from functools import reduce
from typing import Iterable

from domaindrivers.smartschedule.planning.parallelization.parallel_stages import ParallelStages
from domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from domaindrivers.smartschedule.planning.parallelization.stage import Stage


class StageParallelization:
    def of(self, stages: set[Stage]) -> ParallelStagesList:
        return self.create_sorted_nodes_recursively(stages, ParallelStagesList.empty())

    def create_sorted_nodes_recursively(
        self, remaining_nodes: set[Stage], accumulated_sorted_nodes: ParallelStagesList
    ) -> ParallelStagesList:
        already_processed_nodes: list[Stage] = reduce(lambda n, m: list(m.stages), accumulated_sorted_nodes.all, [])

        nodes_without_dependencies: set[Stage] = self.with_all_dependencies_present_in(
            remaining_nodes, already_processed_nodes
        )

        if len(nodes_without_dependencies) == 0:
            return accumulated_sorted_nodes

        new_sorted_nodes: ParallelStagesList = accumulated_sorted_nodes.add(ParallelStages(nodes_without_dependencies))
        new_remaining_nodes: set[Stage] = remaining_nodes.copy()

        def node_reducer(n: set[Stage], m: Stage) -> set[Stage]:
            n.remove(m)
            return n

        new_remaining_nodes = reduce(node_reducer, nodes_without_dependencies, new_remaining_nodes)
        return self.create_sorted_nodes_recursively(new_remaining_nodes, new_sorted_nodes)

    def with_all_dependencies_present_in(self, to_check: set[Stage], present_in: Iterable[Stage]) -> set[Stage]:
        def contains_all(present_in: Iterable[Stage], _to_check: set[Stage]) -> bool:
            if not _to_check:
                return True

            check = [el in present_in for el in _to_check]

            return check != [] and all(check)

        return set(
            filter(lambda n: contains_all(present_in, n.dependencies), to_check),
        )
