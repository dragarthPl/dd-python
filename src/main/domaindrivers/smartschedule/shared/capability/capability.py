from __future__ import annotations

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
    def skills(cls, *skills: str) -> list[Capability]:
        return [Capability.skill(skill) for skill in skills]
