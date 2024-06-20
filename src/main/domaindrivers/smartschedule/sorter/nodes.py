from __future__ import annotations

from typing import Generic, Iterable, TYPE_CHECKING, TypeGuard, TypeVar

from attrs import frozen

if TYPE_CHECKING:
    from domaindrivers.smartschedule.sorter.node import Node

T = TypeVar("T")


@frozen
class Nodes(Generic[T]):
    nodes: set["Node[T]"]

    def all(self) -> frozenset["Node[T]"]:
        return frozenset(self.nodes)

    def add(self, node: "Node[T]") -> "Nodes[T]":
        new_node = self.nodes.copy()
        new_node = new_node.union({node})
        return Nodes[T](new_node)

    def with_all_dependencies_present_in(self, nodes: Iterable["Node[T]"]) -> "Nodes[T]":
        def contains_all(n: "Node[T]") -> TypeGuard[bool]:
            present_in: Iterable["Node[T]"] = nodes
            _to_check: set["Node[T]"] = set(n.dependencies.all())

            if not _to_check:
                return True

            check = [el in present_in for el in _to_check]

            return check != [] and all(check)

        return Nodes[T](set(filter(contains_all, self.all())))

    def remove_all(self, nodes: Iterable["Node[T]"]) -> Nodes[T]:
        return Nodes[T](set(filter(lambda s: s not in nodes, self.all())))

    def __str__(self) -> str:
        return f"Nodes{{node={self.nodes}}}"
