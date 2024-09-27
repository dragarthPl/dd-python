from abc import ABC, abstractmethod
from datetime import datetime

from domaindrivers.smartschedule.allocation.project_allocations import ProjectAllocations
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.utils.optional import Optional


class ProjectAllocationsRepository(ABC):
    @abstractmethod
    def find_all_containing_date(self, when: datetime) -> list[ProjectAllocations]: ...

    @abstractmethod
    def find_by_id(self, project_id: ProjectAllocationsId) -> Optional[ProjectAllocations]: ...

    @abstractmethod
    def save(self, project: ProjectAllocations) -> ProjectAllocations: ...

    @abstractmethod
    def find_all_by_id(self, project_ids: set[ProjectAllocationsId]) -> list[ProjectAllocations]: ...

    @abstractmethod
    def find_all(self) -> list[ProjectAllocations]: ...
