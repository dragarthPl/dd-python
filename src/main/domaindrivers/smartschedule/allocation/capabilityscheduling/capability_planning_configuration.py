from typing import cast, Type

import injector
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_repository import (
    AllocatableCapabilityRepository,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_repository_sqlalchemy import (
    AllocatableCapabilityRepositorySqlalchemy,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.capability_finder import CapabilityFinder
from domaindrivers.smartschedule.allocation.capabilityscheduling.capability_scheduler import CapabilityScheduler
from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from injector import Module, provider, singleton
from sqlalchemy.orm import Session


class CapabilityPlanningConfiguration(Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(
            cast(Type[AllocatableCapabilityRepository], AllocatableCapabilityRepository),
            to=AllocatableCapabilityRepositorySqlalchemy,
        )
        pass

    @provider
    @singleton
    def capability_scheduler(
        self,
        session: Session,
        availability_facade: AvailabilityFacade,
        allocatable_resource_repository: AllocatableCapabilityRepository,
    ) -> CapabilityScheduler:
        return CapabilityScheduler(session, availability_facade, allocatable_resource_repository)

    @provider
    @singleton
    def capability_finder(
        self, availability_facade: AvailabilityFacade, allocatable_resource_repository: AllocatableCapabilityRepository
    ) -> CapabilityFinder:
        return CapabilityFinder(availability_facade, allocatable_resource_repository)
