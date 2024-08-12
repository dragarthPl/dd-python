import hashlib
import uuid
from typing import Any

from attrs import field, frozen
from domaindrivers.utils.serializable import Serializable


@frozen
class ProjectAllocationsId(Serializable):
    __project_allocations_id: uuid.UUID = field(default=None)

    @classmethod
    def new_one(cls) -> "ProjectAllocationsId":
        return ProjectAllocationsId(uuid.uuid4())

    def id(self) -> uuid.UUID:
        return self.__project_allocations_id

    def __composite_values__(self) -> tuple[uuid.UUID]:
        return (self.__project_allocations_id,)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ProjectAllocationsId):
            return False
        return self.__project_allocations_id == other.__project_allocations_id

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.__project_allocations_id).encode("utf-8"))

        return int(m.hexdigest(), 16)
