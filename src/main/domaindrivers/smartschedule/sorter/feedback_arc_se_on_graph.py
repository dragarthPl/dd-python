from attrs import frozen
from domaindrivers.smartschedule.sorter.node import Node


class FeedbackArcSeOnGraph:
    @classmethod
    def calculate(cls, initial_nodes: list["Node[str]"]) -> list["Edge"]:
        adjacency_list: dict[int, list[int]] = cls.__create_adjacency_list(initial_nodes)
        v: int = len(adjacency_list)
        feedback_edges: list[Edge] = []
        visited: list[int | None] = [None for _ in range(v + 1)]
        for key in adjacency_list:
            i = key
            neighbours: list[int] = adjacency_list[i]
            if len(neighbours) != 0:
                visited[i] = 1
                for neighbour in neighbours:
                    if visited[neighbour] == 1:
                        feedback_edges.append(Edge(i, neighbour))
                    else:
                        visited[neighbour] = 1
        return feedback_edges

    @staticmethod
    def __create_adjacency_list(initial_nodes: list["Node[str]"]) -> dict[int, list[int]]:
        adjacency_list: dict[int, list[int]] = {}
        for i, node in enumerate(initial_nodes):
            adjacency_list[i + 1] = []

        for i, node in enumerate(initial_nodes):
            dependencies: list[int] = []
            for dependency in node.dependencies.nodes:
                dependencies.append(initial_nodes.index(dependency) + 1)
            adjacency_list[i + 1] = dependencies
        return adjacency_list


@frozen
class Edge:
    source: int
    target: int

    def __str__(self) -> str:
        return f"({self.source} -> {self.target})"
