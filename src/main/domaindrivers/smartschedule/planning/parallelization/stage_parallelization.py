from attr import frozen
from domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from domaindrivers.smartschedule.planning.parallelization.sorted_nodes_to_parallelized_stages import (
    SortedNodesToParallelizedStages,
)
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.parallelization.stages_to_nodes import StagesToNodes
from domaindrivers.smartschedule.sorter.edge import Edge
from domaindrivers.smartschedule.sorter.feedback_arc_se_on_graph import FeedbackArcSeOnGraph
from domaindrivers.smartschedule.sorter.graph_topological_sort import GraphTopologicalSort
from domaindrivers.smartschedule.sorter.nodes import Nodes
from domaindrivers.smartschedule.sorter.sorted_nodes import SortedNodes


@frozen
class RemovalSuggestion:
    edges: list[Edge]

    def to_string(self) -> str:
        return str([edge.to_string() for edge in self.edges])


class StageParallelization:
    def of(self, stages: set[Stage]) -> ParallelStagesList:
        nodes: Nodes[Stage] = StagesToNodes().calculate(list(stages))

        sorted_nodes: SortedNodes[Stage] = GraphTopologicalSort[Stage]().sort(nodes)
        return SortedNodesToParallelizedStages().calculate(sorted_nodes)

    def what_to_remove(self, stages: set[Stage]) -> RemovalSuggestion:
        nodes: Nodes[Stage] = StagesToNodes().calculate(list(stages))
        result: list[Edge] = FeedbackArcSeOnGraph[Stage]().calculate(list(nodes.nodes))
        return RemovalSuggestion(result)
