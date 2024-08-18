import hashlib
import uuid
from typing import Any
from uuid import UUID

from domaindrivers.utils.serializable import Serializable


class ResourceId(Serializable):
    __resource_id: UUID

    def __init__(self, resource_id: UUID = None):
        self.__resource_id = resource_id

    @classmethod
    def new_one(cls) -> "ResourceId":
        return cls(uuid.uuid4())

    @classmethod
    def none(cls) -> "ResourceId":
        return cls(None)

    @classmethod
    def of(cls, resource_id: UUID) -> "ResourceId":
        if not resource_id:
            return cls.none()
        return cls(resource_id)

    def get_id(self) -> UUID:
        return self.__resource_id

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ResourceId):
            return False
        return self.__resource_id == other.get_id()

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.__resource_id).encode("utf-8"))

        return int(m.hexdigest(), 16)
