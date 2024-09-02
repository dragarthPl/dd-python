import hashlib
import uuid
from typing import Any
from uuid import UUID

from attr import frozen
from domaindrivers.utils.serializable import Serializable


@frozen
class AllocatableResourceId(Serializable):
    __allocatable_resource_id: UUID

    @classmethod
    def new_one(cls) -> "AllocatableResourceId":
        return cls(uuid.uuid4())

    def id(self) -> UUID:
        return self.__allocatable_resource_id

    def __composite_values__(self) -> tuple[uuid.UUID]:
        return (self.__allocatable_resource_id,)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AllocatableResourceId):
            return False
        return self.__allocatable_resource_id == other.__allocatable_resource_id

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.__allocatable_resource_id).encode("utf-8"))

        return int(m.hexdigest(), 16)
