import injector
from domaindrivers.smartschedule.allocation.allocation_facade import AllocationFacade
from domaindrivers.smartschedule.allocation.project_allocations_repository import ProjectAllocationsRepository
from domaindrivers.smartschedule.allocation.project_allocations_repository_impl import ProjectAllocationsRepositoryImpl
from injector import Module, provider, singleton
from sqlalchemy.orm import Session


class AllocationConfiguration(Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(ProjectAllocationsRepository, to=ProjectAllocationsRepositoryImpl)
        pass

    @singleton
    @provider
    def planning_facade(
        self,
        session: Session,
        project_allocations_repository: ProjectAllocationsRepository,
    ) -> AllocationFacade:
        return AllocationFacade(session, project_allocations_repository)
