import hashlib
import uuid
from typing import Any
from uuid import UUID

from domaindrivers.utils.serializable import Serializable


class ResourceId(Serializable):
    __resource_id: UUID

    @classmethod
    def new_one(cls) -> "ResourceId":
        return cls(uuid.uuid4())

    def __init__(self, resource_id: UUID):
        self.__resource_id = resource_id

    @classmethod
    def from_key(cls, key: UUID) -> "ResourceId":
        return cls(key)

    def id(self) -> UUID:
        return self.__resource_id

    def __composite_values__(self) -> tuple[UUID]:
        return (self.__resource_id,)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ResourceId):
            return False
        return self.__resource_id == other.__resource_id

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.__resource_id).encode("utf-8"))

        return int(m.hexdigest(), 16)
