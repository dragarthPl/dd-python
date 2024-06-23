from domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from domaindrivers.smartschedule.planning.parallelization.sorted_nodes_to_parallelized_stages import (
    SortedNodesToParallelizedStages,
)
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.parallelization.stages_to_nodes import StagesToNodes
from domaindrivers.smartschedule.sorter.graph_topological_sort import GraphTopologicalSort
from domaindrivers.smartschedule.sorter.nodes import Nodes
from domaindrivers.smartschedule.sorter.sorted_nodes import SortedNodes
from domaindrivers.utils.functional import Function


class StageParallelization:
    __CREATE_NODES = Function[list[Stage], Nodes[Stage]](lambda stages: StagesToNodes().apply(stages))
    __GRAPH_SORT = Function[Nodes[Stage], SortedNodes[Stage]](lambda nodes: GraphTopologicalSort[Stage]().apply(nodes))
    __PARALLELIZE = Function[SortedNodes[Stage], ParallelStagesList](
        lambda nodes: SortedNodesToParallelizedStages().apply(nodes)
    )

    __WORKFLOW = Function[list[Stage], ParallelStagesList](
        __CREATE_NODES.and_then(__GRAPH_SORT).and_then(__PARALLELIZE)
    )

    def of(self, stages: set[Stage]) -> ParallelStagesList:
        return self.__WORKFLOW.apply(list(stages))
