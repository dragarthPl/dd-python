import hashlib
import uuid
from typing import Any

from domaindrivers.utils.serializable import Serializable


class ProjectAllocationsId(Serializable):
    __project_allocations_id: uuid.UUID

    @classmethod
    def new_one(cls) -> "ProjectAllocationsId":
        return ProjectAllocationsId(uuid.uuid4())

    def __init__(self, project_allocations_id: uuid.UUID = None):
        if project_allocations_id is not None:
            self.__project_allocations_id = project_allocations_id

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
