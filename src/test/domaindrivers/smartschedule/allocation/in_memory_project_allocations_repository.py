from datetime import datetime
from typing import Final

from domaindrivers.smartschedule.allocation.project_allocations import ProjectAllocations
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.allocation.project_allocations_repository import ProjectAllocationsRepository
from domaindrivers.utils.optional import Optional


class InMemoryProjectAllocationsRepository(ProjectAllocationsRepository):
    __projects: Final[dict[ProjectAllocationsId, ProjectAllocations]]

    def __init__(self) -> None:
        self.__projects = {}

    def find_by_id(self, project_id: ProjectAllocationsId) -> Optional[ProjectAllocations]:
        return Optional.of_nullable(self.__projects.get(project_id, None))

    def save(self, project: ProjectAllocations) -> ProjectAllocations:
        self.__projects[project.id] = project
        return self.__projects[project.id]

    def find_all_by_id(self, project_ids: set[ProjectAllocationsId]) -> list[ProjectAllocations]:
        return list(filter(lambda project: project.id in project_ids, self.__projects.values()))

    def find_all(self) -> list[ProjectAllocations]:
        return list(self.__projects.values())

    def find_all_containing_date(self, when: datetime) -> list[ProjectAllocations]:
        return list(filter(lambda project: project.time_slot() is not None, self.__projects.values()))
