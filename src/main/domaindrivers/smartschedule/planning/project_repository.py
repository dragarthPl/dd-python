from abc import ABC, abstractmethod

from domaindrivers.smartschedule.planning.project import Project
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.utils.optional import Optional


class ProjectRepository(ABC):
    @abstractmethod
    def find_by_id(self, project_id: ProjectId) -> Optional[Project]: ...

    @abstractmethod
    def save(self, project: Project) -> Project: ...

    @abstractmethod
    def find_all_by_id_in(self, project_id: set[ProjectId]) -> list[Project]: ...

    @abstractmethod
    def find_all(self) -> list[Project]: ...
