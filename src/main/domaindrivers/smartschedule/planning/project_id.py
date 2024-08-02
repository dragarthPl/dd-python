import hashlib
import uuid
from typing import Any
from uuid import UUID

from attr import field, frozen
from domaindrivers.utils.serializable import Serializable


@frozen
class ProjectId(Serializable):
    __project_id: UUID = field(default=None)

    @classmethod
    def new_one(cls) -> "ProjectId":
        return cls(uuid.uuid4())

    @classmethod
    def of(cls, project_id: UUID) -> "ProjectId":
        return cls(project_id)

    def id(self) -> UUID:
        return self.__project_id

    def __composite_values__(self) -> tuple[UUID]:
        return (self.__project_id,)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ProjectId):
            return False
        return self.__project_id == other.__project_id

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.__project_id).encode("utf-8"))

        return int(m.hexdigest(), 16)
