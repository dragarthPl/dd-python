from __future__ import annotations

from typing import Iterable, TYPE_CHECKING, TypeGuard

from attrs import frozen

if TYPE_CHECKING:
    from domaindrivers.smartschedule.sorter.node import Node


@frozen
class Nodes:
    nodes: set["Node"]

    def all(self) -> frozenset["Node"]:
        return frozenset(self.nodes)

    def add(self, node: "Node") -> "Nodes":
        new_node = self.nodes.copy()
        new_node = new_node.union({node})
        return Nodes(new_node)

    def with_all_dependencies_present_in(self, nodes: Iterable["Node"]) -> "Nodes":
        def contains_all(n: "Node") -> TypeGuard[bool]:
            present_in: Iterable["Node"] = nodes
            _to_check: set["Node"] = set(n.dependencies.all())

            if not _to_check:
                return True

            check = [el in present_in for el in _to_check]

            return check != [] and all(check)

        return Nodes(set(filter(contains_all, self.all())))

    def remove_all(self, nodes: Iterable["Node"]) -> Nodes:
        return Nodes(set(filter(lambda s: s not in nodes, self.all())))

    def __str__(self) -> str:
        return f"Nodes{{node={self.nodes}}}"
