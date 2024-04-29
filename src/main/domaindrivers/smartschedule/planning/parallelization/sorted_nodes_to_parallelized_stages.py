from src.main.domaindrivers.smartschedule.planning.parallelization.parallel_stages import ParallelStages
from src.main.domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from src.main.domaindrivers.smartschedule.sorter.sorted_nodes import SortedNodes


class SortedNodesToParallelizedStages:
    def calculate(self, sorted_nodes: SortedNodes) -> ParallelStagesList:
        parallelized: list[ParallelStages] = list(
            map(lambda nodes: ParallelStages(set(map(lambda node: node.content, nodes.nodes))), sorted_nodes.all)
        )
        return ParallelStagesList(parallelized)
