from typing import cast, Type

import injector
from domaindrivers.smartschedule.allocation.allocation_facade import AllocationFacade
from domaindrivers.smartschedule.allocation.project_allocations_repository import ProjectAllocationsRepository
from domaindrivers.smartschedule.allocation.project_allocations_repository_sqlalchemy import (
    ProjectAllocationsRepositorySqlalchemy,
)
from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from injector import Module, provider, singleton
from sqlalchemy.orm import Session


class AllocationConfiguration(Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(
            cast(Type[ProjectAllocationsRepository], ProjectAllocationsRepository),
            to=ProjectAllocationsRepositorySqlalchemy,
        )
        pass

    @singleton
    @provider
    def planning_facade(
        self,
        session: Session,
        project_allocations_repository: ProjectAllocationsRepository,
        availability_facade: AvailabilityFacade,
    ) -> AllocationFacade:
        return AllocationFacade(session, project_allocations_repository, availability_facade)
