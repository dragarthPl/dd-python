from typing import Final
from unittest import TestCase

from domaindrivers.smartschedule.sorter.graph_topological_sort import GraphTopologicalSort
from domaindrivers.smartschedule.sorter.node import Node
from domaindrivers.smartschedule.sorter.nodes import Nodes
from domaindrivers.smartschedule.sorter.sorted_nodes import SortedNodes


class TestGraphTopologicalSort(TestCase):
    GRAPH_TOPOLOGICAL_SORT: Final[GraphTopologicalSort] = GraphTopologicalSort()

    def test_topological_sort_with_simple_dependencies(self) -> None:
        # given

        node1: Node = Node.from_name("Node1")

        node2: Node = Node.from_name("Node2")

        node3: Node = Node.from_name("Node3")

        node4: Node = Node.from_name("Node4")
        node2 = node2.depends_on(node1)
        node3 = node3.depends_on(node1)
        node4 = node4.depends_on(node2)

        nodes: Nodes = Nodes({node1, node2, node3, node4})

        # when
        sorted_nodes: SortedNodes = self.GRAPH_TOPOLOGICAL_SORT.sort(nodes)

        # then
        self.assertEqual(3, len(sorted_nodes.all))

        self.assertEqual(1, len(sorted_nodes.all[0].nodes))
        self.assertTrue(node1 in sorted_nodes.all[0].nodes)

        self.assertEqual(2, len(sorted_nodes.all[1].nodes))
        self.assertTrue(node2 in sorted_nodes.all[1].nodes)
        self.assertTrue(node3 in sorted_nodes.all[1].nodes)

        self.assertEqual(1, len(sorted_nodes.all[2].nodes))
        self.assertTrue(node4 in sorted_nodes.all[2].nodes)

    def test_topological_sort_with_linear_dependencies(self) -> None:
        # given
        node1: Node = Node.from_name("Node1")
        node2: Node = Node.from_name("Node2")
        node3: Node = Node.from_name("Node3")
        node4: Node = Node.from_name("Node4")
        node5: Node = Node.from_name("Node5")
        node1 = node1.depends_on(node2)
        node2 = node2.depends_on(node3)
        node3 = node3.depends_on(node4)
        node4 = node4.depends_on(node5)

        nodes: Nodes = Nodes({node1, node2, node3, node4, node5})

        # when
        sorted_nodes: SortedNodes = self.GRAPH_TOPOLOGICAL_SORT.sort(nodes)

        # then
        self.assertEqual(5, len(sorted_nodes.all))

        self.assertEqual(1, len(sorted_nodes.all[0].nodes))
        self.assertTrue(node5 in sorted_nodes.all[0].nodes)

        self.assertEqual(1, len(sorted_nodes.all[1].nodes))
        self.assertTrue(node4 in sorted_nodes.all[1].nodes)

        self.assertEqual(1, len(sorted_nodes.all[2].nodes))
        self.assertTrue(node3 in sorted_nodes.all[2].nodes)

        self.assertEqual(1, len(sorted_nodes.all[3].nodes))
        self.assertTrue(node2 in sorted_nodes.all[3].nodes)

        self.assertEqual(1, len(sorted_nodes.all[4].nodes))
        self.assertTrue(node1 in sorted_nodes.all[4].nodes)

    def test_nodes_without_dependencies(self) -> None:
        # given
        node1: Node = Node.from_name("Node1")
        node2: Node = Node.from_name("Node2")
        nodes: Nodes = Nodes({node1, node2})

        # when
        sorted_nodes: SortedNodes = self.GRAPH_TOPOLOGICAL_SORT.sort(nodes)

        # then
        self.assertEqual(1, len(sorted_nodes.all))

    def test_cyclic_dependency(self) -> None:
        # given
        node1: Node = Node.from_name("Node1")
        node2: Node = Node.from_name("Node2")
        node2 = node2.depends_on(node1)
        node1 = node1.depends_on(node2)  # making it cyclic
        nodes: Nodes = Nodes({node1, node2})

        # when
        sorted_nodes: SortedNodes = self.GRAPH_TOPOLOGICAL_SORT.sort(nodes)

        # then
        self.assertTrue(sorted_nodes.all == [])
