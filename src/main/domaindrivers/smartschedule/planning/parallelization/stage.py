import hashlib
from datetime import timedelta
from typing import Any

from attr import frozen


@frozen
class ResourceName:
    name: str


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
        self.dependencies.add(stage)
        return self

    @property
    def name(self) -> str:
        return self.stage_name

    def __eq__(self, other: Any) -> bool:
        if other is None or not isinstance(other, Stage):
            return False
        return bool(self.stage_name == other.name)

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.stage_name).encode("utf-8"))

        return int(m.hexdigest(), 16)
