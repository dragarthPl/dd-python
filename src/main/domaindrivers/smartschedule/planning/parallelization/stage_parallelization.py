from domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from domaindrivers.smartschedule.planning.parallelization.sorted_nodes_to_parallelized_stages import (
    SortedNodesToParallelizedStages,
)
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.parallelization.stages_to_nodes import StagesToNodes
from domaindrivers.smartschedule.sorter.graph_topological_sort import GraphTopologicalSort
from domaindrivers.smartschedule.sorter.nodes import Nodes
from domaindrivers.smartschedule.sorter.sorted_nodes import SortedNodes


class StageParallelization:
    def of(self, stages: set[Stage]) -> ParallelStagesList:
        nodes: Nodes = StagesToNodes().calculate(list(stages))

        sorted_nodes: SortedNodes = GraphTopologicalSort().sort(nodes)
        return SortedNodesToParallelizedStages().calculate(sorted_nodes)
