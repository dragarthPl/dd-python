import hashlib
import uuid
from typing import Any

from attr import field, frozen
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_resource_id import AllocatableResourceId
from domaindrivers.utils.serializable import Serializable


@frozen
class DeviceId(Serializable):
    __device_id: uuid.UUID = field(default=None)

    @classmethod
    def new_one(cls) -> "DeviceId":
        return cls(uuid.uuid4())

    def id(self) -> uuid.UUID:
        return self.__device_id

    def to_allocatable_resource_id(self) -> AllocatableResourceId:
        return AllocatableResourceId(self.__device_id)

    def __composite_values__(self) -> tuple[uuid.UUID]:
        return (self.__device_id,)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, DeviceId):
            return False
        return self.__device_id == other.__device_id

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.__device_id).encode("utf-8"))

        return int(m.hexdigest(), 16)
