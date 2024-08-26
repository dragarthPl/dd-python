import hashlib
import uuid
from typing import Any
from uuid import UUID

from attr import frozen
from domaindrivers.utils.serializable import Serializable


@frozen
class EmployeeId(Serializable):
    __employee_id: UUID

    @classmethod
    def new_one(cls) -> "EmployeeId":
        return cls(uuid.uuid4())

    def id(self) -> UUID:
        return self.__employee_id

    def __composite_values__(self) -> tuple[UUID]:
        return (self.__employee_id,)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, EmployeeId):
            return False
        return self.__employee_id == other.__employee_id

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.__employee_id).encode("utf-8"))

        return int(m.hexdigest(), 16)
