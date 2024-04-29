from functools import reduce

from domaindrivers.smartschedule.sorter.node import Node
from domaindrivers.smartschedule.sorter.nodes import Nodes
from domaindrivers.smartschedule.sorter.sorted_nodes import SortedNodes


class GraphTopologicalSort:
    def sort(self, nodes: Nodes) -> SortedNodes:
        return self.create_sorted_nodes_recursively(nodes, SortedNodes.empty())

    def create_sorted_nodes_recursively(
        self, remaining_nodes: Nodes, accumulated_sorted_nodes: SortedNodes
    ) -> SortedNodes:
        already_processed_nodes: list[Node] = reduce(lambda n, m: list(m.all()), accumulated_sorted_nodes.all, [])
        nodes_without_dependencies = remaining_nodes.with_all_dependencies_present_in(already_processed_nodes)
        if len(nodes_without_dependencies.all()) == 0:
            return accumulated_sorted_nodes
        new_sorted_nodes = accumulated_sorted_nodes.add(nodes_without_dependencies)
        remaining_nodes = remaining_nodes.remove_all(nodes_without_dependencies.all())
        return self.create_sorted_nodes_recursively(remaining_nodes, new_sorted_nodes)
