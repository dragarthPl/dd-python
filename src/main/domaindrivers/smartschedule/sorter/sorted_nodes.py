from typing import Generic, TypeVar

from attrs import frozen
from domaindrivers.smartschedule.sorter.nodes import Nodes

T = TypeVar("T")


@frozen
class SortedNodes(Generic[T]):
    all: list[Nodes[T]]

    @classmethod
    def empty(cls) -> "SortedNodes[T]":
        return cls([])

    def add(self, new_node: Nodes[T]) -> "SortedNodes[T]":
        result: list[Nodes[T]] = self.all + [new_node]
        return SortedNodes(result)

    def __str__(self) -> str:
        return f"SortedNodes: {self.all}"
