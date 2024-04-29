from unittest import TestCase

from domaindrivers.smartschedule.sorter.feedback_arc_se_on_graph import Edge, FeedbackArcSeOnGraph
from domaindrivers.smartschedule.sorter.node import Node


class TestFeedbackArcSetOnGraph(TestCase):
    def test_can_find_minimum_number_of_edges_to_remove_to_make_the_graph_acyclic(self) -> None:
        # given
        node1: Node = Node.from_name("1")
        node2: Node = Node.from_name("2")
        node3: Node = Node.from_name("3")
        node4: Node = Node.from_name("4")
        node1 = node1.depends_on(node2)
        node2 = node2.depends_on(node3)
        node4 = node4.depends_on(node3)
        node1 = node1.depends_on(node4)
        node3 = node3.depends_on(node1)

        # when
        to_remove: list[Edge] = FeedbackArcSeOnGraph.calculate([node1, node2, node3, node4])

        self.assertIn(Edge(4, 3), to_remove)
        self.assertIn(Edge(3, 1), to_remove)
        self.assertEqual(2, len(to_remove))

    def test_when_graph_is_acyclic_there_is_nothing_to_remove(self) -> None:
        # given

        node1: Node = Node.from_name("1")

        node2: Node = Node.from_name("2")

        node3: Node = Node.from_name("3")

        node4: Node = Node.from_name("4")
        node1 = node1.depends_on(node2)
        node2 = node2.depends_on(node3)
        node1 = node1.depends_on(node4)

        # when
        to_remove: list[Edge] = FeedbackArcSeOnGraph.calculate([node1, node2, node3, node4])

        # then
        self.assertListEqual(to_remove, [])
