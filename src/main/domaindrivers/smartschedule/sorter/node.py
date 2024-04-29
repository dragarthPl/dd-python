import hashlib
from typing import Any

from attrs import frozen
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.sorter.nodes import Nodes


@frozen
class Node:
    name: str
    dependencies: Nodes
    content: Stage | None

    @classmethod
    def from_name(cls, name: str) -> "Node":
        return cls(name, Nodes(set()), None)

    @classmethod
    def from_name_stage(cls, name: str, content: Stage) -> "Node":
        return cls(name, Nodes(set()), content)

    def depends_on(self, node: "Node") -> "Node":
        return Node(self.name, self.dependencies.add(node), self.content)

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: Any) -> bool:
        if other is None or not isinstance(other, Node):
            return False
        return bool(self.name == other.name)

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.name).encode("utf-8"))

        return int(m.hexdigest(), 16)
