from typing import TYPE_CHECKING

from domaindrivers.smartschedule.planning.parallelization.parallel_stages import ParallelStages
from domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.sorter.sorted_nodes import SortedNodes

if TYPE_CHECKING:
    from src.main.domaindrivers.utils.functional import Function
else:
    from domaindrivers.utils.functional import Function


class SortedNodesToParallelizedStages(Function[SortedNodes[Stage], ParallelStagesList]):
    def apply(self, sorted_nodes: SortedNodes[Stage]) -> ParallelStagesList:
        parallelized: list[ParallelStages] = list(
            map(lambda nodes: ParallelStages(set(map(lambda node: node.content, nodes.nodes))), sorted_nodes.all)
        )
        return ParallelStagesList(parallelized)
