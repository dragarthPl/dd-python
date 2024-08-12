from domaindrivers.smartschedule.allocation.project_allocations import ProjectAllocations
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.storage.repository import Repository


class ProjectAllocationsRepository(Repository[ProjectAllocations, ProjectAllocationsId]):
    pass
