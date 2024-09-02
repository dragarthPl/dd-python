import hashlib
import uuid
from typing import Any

from attr import frozen
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.utils.serializable import Serializable


@frozen
class AllocatableCapabilityId(Serializable):
    __id: uuid.UUID = None

    @classmethod
    def new_one(cls) -> "AllocatableCapabilityId":
        return cls(uuid.uuid4())

    @classmethod
    def none(cls) -> "AllocatableCapabilityId":
        return cls(None)

    def __composite_values__(self) -> tuple[uuid.UUID]:
        return (self.__id,)

    def get_id(self) -> uuid.UUID:
        return self.__id

    def to_availability_resource_id(self) -> ResourceId:
        return ResourceId.of(self.__id)

    @classmethod
    def from_resource_id(cls, resource_id: ResourceId) -> "AllocatableCapabilityId":
        return cls(resource_id.get_id())

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AllocatableCapabilityId):
            return False
        return self.__id == other.__id

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.__id).encode("utf-8"))

        return int(m.hexdigest(), 16)
