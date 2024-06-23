from functools import reduce
from typing import Callable, Generic, TypeVar

from domaindrivers.smartschedule.sorter.node import Node
from domaindrivers.smartschedule.sorter.nodes import Nodes
from domaindrivers.smartschedule.sorter.sorted_nodes import SortedNodes
from domaindrivers.utils.functional import BiFunction, Function

T = TypeVar("T")
R = TypeVar("R")


class GraphTopologicalSort(Generic[T], Function[Nodes[T], SortedNodes[T]]):
    __create_sorted_nodes_recursively: BiFunction[Nodes[T], SortedNodes[T], SortedNodes[T]]

    def __init__(self, function: Callable[[T], R] = None):
        self.__create_sorted_nodes_recursively = IntermediateSortedNodesCreator()

    def apply(self, stages: Nodes[T]) -> SortedNodes[T]:
        return self.__create_sorted_nodes_recursively.apply(stages, SortedNodes.empty())


class IntermediateSortedNodesCreator(Generic[T], BiFunction[Nodes[T], SortedNodes[T], SortedNodes[T]]):
    def apply(self, remaining_nodes: Nodes[T], accumulated_sorted_nodes: SortedNodes[T]) -> SortedNodes[T]:
        already_processed_nodes: list[Node[T]] = reduce(lambda n, m: list(m.all()), accumulated_sorted_nodes.all, [])
        nodes_without_dependencies = remaining_nodes.with_all_dependencies_present_in(already_processed_nodes)
        if len(nodes_without_dependencies.all()) == 0:
            return accumulated_sorted_nodes
        new_sorted_nodes = accumulated_sorted_nodes.add(nodes_without_dependencies)
        remaining_nodes = remaining_nodes.remove_all(nodes_without_dependencies.all())
        return self.apply(remaining_nodes, new_sorted_nodes)
