import hashlib
import uuid
from typing import Any, cast

from attr import field, frozen
from domaindrivers.storage.uuid_pg import UUID
from domaindrivers.utils.serializable import Serializable


@frozen
class DeviceId(Serializable):  # type: ignore
    __device_id: UUID = field(default=None)

    @classmethod
    def new_one(cls) -> "DeviceId":
        return cls(uuid.uuid4())

    def id(self) -> UUID:
        return self.__device_id

    def __composite_values__(self) -> tuple[UUID]:
        return (self.__device_id,)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, DeviceId):
            return False
        return cast(bool, self.__device_id == other.__device_id)

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.__device_id).encode("utf-8"))

        return int(m.hexdigest(), 16)
