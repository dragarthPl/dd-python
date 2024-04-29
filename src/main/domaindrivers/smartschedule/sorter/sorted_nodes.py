from attrs import frozen
from domaindrivers.smartschedule.sorter.nodes import Nodes


@frozen
class SortedNodes:
    all: list[Nodes]

    @classmethod
    def empty(cls) -> "SortedNodes":
        return cls([])

    def add(self, new_node: Nodes) -> "SortedNodes":
        result: list[Nodes] = self.all + [new_node]
        return SortedNodes(result)

    def __str__(self) -> str:
        return f"SortedNodes: {self.all}"
