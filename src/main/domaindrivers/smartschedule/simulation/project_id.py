import uuid
from uuid import UUID

from domaindrivers.utils.serializable import Serializable


class ProjectId(Serializable):
    __project_id: UUID

    @classmethod
    def new_one(cls) -> "ProjectId":
        return cls(uuid.uuid4())

    def __init__(self, project_id: UUID):
        self.__project_id = project_id

    def id(self) -> UUID:
        return self.__project_id
