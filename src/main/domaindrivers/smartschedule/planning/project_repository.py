from domaindrivers.smartschedule.allocation.project import Project
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.storage.repository import Repository


class ProjectRepository(Repository[Project, ProjectId]):  # type: ignore
    pass
