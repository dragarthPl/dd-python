from __future__ import annotations

import hashlib
from typing import Any

from attr import frozen
from domaindrivers.utils.serializable import Serializable


@frozen
class Capability(Serializable):
    name: str
    type: str

    @classmethod
    def skill(cls, name: str) -> "Capability":
        return cls(name, "SKILL")

    @classmethod
    def permission(cls, name: str) -> "Capability":
        return cls(name, "PERMISSION")

    @classmethod
    def asset(cls, asset: str) -> "Capability":
        return cls(asset, "ASSET")

    @classmethod
    def skills(cls, *skills: str) -> set[Capability]:
        return {Capability.skill(skill) for skill in skills}

    @classmethod
    def assets(cls, *assets: str) -> set[Capability]:
        return {cls.asset(asset) for asset in assets}

    @classmethod
    def permissions(cls, *permissions: str) -> set[Capability]:
        return {cls.permission(permission) for permission in permissions}

    def is_of_type(self, of_type: str) -> bool:
        return self.type == of_type

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Capability):
            return False
        return self.name == other.name and self.type == other.type

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.name).encode("utf-8"))
        m.update(str(self.type).encode("utf-8"))

        return int(m.hexdigest(), 16)
