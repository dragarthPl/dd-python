import hashlib
from datetime import timedelta
from typing import Any

from attr import frozen


@frozen
class ResourceName:
    name: str

    def __eq__(self, other: Any) -> bool:
        if other is None or not isinstance(other, ResourceName):
            return False
        return bool(self.name == other.name)

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.name).encode("utf-8"))

        return int(m.hexdigest(), 16)


@frozen
class Stage:
    stage_name: str
    dependencies: set["Stage"]
    resources: set[ResourceName]
    duration: timedelta

    @classmethod
    def from_name(cls, stage_name: str) -> "Stage":
        return cls(stage_name, set(), set(), timedelta())

    def depends_on(self, stage: "Stage") -> "Stage":
        new_dependencies: set[Stage] = set(self.dependencies)
        new_dependencies.add(stage)
        self.dependencies.add(stage)
        return Stage(self.stage_name, new_dependencies, self.resources, self.duration)

    @property
    def name(self) -> str:
        return self.stage_name

    def with_chosen_resource_capabilities(self, *resources: ResourceName) -> "Stage":
        collect: set[ResourceName] = set(resources)
        return Stage(self.stage_name, self.dependencies, collect, self.duration)

    def __eq__(self, other: Any) -> bool:
        if other is None or not isinstance(other, Stage):
            return False
        return bool(self.stage_name == other.name)

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.stage_name).encode("utf-8"))

        return int(m.hexdigest(), 16)
