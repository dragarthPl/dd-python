from typing import cast

import injector
from domaindrivers.smartschedule.allocation.allocation_facade import AllocationFacade
from domaindrivers.smartschedule.allocation.capabilityscheduling.capability_finder import CapabilityFinder
from domaindrivers.smartschedule.allocation.cashflow.cash_flow_facade import CashFlowFacade
from domaindrivers.smartschedule.allocation.potential_transfers_service import PotentialTransfersService
from domaindrivers.smartschedule.allocation.project_allocations_repository import ProjectAllocationsRepository
from domaindrivers.smartschedule.allocation.project_allocations_repository_sqlalchemy import (
    ProjectAllocationsRepositorySqlalchemy,
)
from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher
from domaindrivers.smartschedule.simulation.simulation_facade import SimulationFacade
from injector import Module, provider, singleton
from sqlalchemy.orm import Session


class AllocationConfiguration(Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(
            cast(type[ProjectAllocationsRepository], ProjectAllocationsRepository),
            to=ProjectAllocationsRepositorySqlalchemy,
        )

    @singleton
    @provider
    def planning_facade(
        self,
        session: Session,
        project_allocations_repository: ProjectAllocationsRepository,
        availability_facade: AvailabilityFacade,
        capability_finder: CapabilityFinder,
        events_publisher: EventsPublisher,
    ) -> AllocationFacade:
        return AllocationFacade(
            session, project_allocations_repository, availability_facade, capability_finder, events_publisher
        )

    @singleton
    @provider
    def potential_transfers_service(
        self,
        cash_flow_facade: CashFlowFacade,
        project_allocations_repository: ProjectAllocationsRepository,
    ) -> PotentialTransfersService:
        return PotentialTransfersService(SimulationFacade(), cash_flow_facade, project_allocations_repository)
