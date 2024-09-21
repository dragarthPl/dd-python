from typing import Final

from domaindrivers.smartschedule.allocation.allocated_capability import AllocatedCapability
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_summary import (
    AllocatableCapabilitySummary,
)
from domaindrivers.smartschedule.allocation.cashflow.cash_flow_facade import CashFlowFacade
from domaindrivers.smartschedule.allocation.potential_transfers import PotentialTransfers
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.allocation.project_allocations_repository import ProjectAllocationsRepository
from domaindrivers.smartschedule.allocation.projects_allocations_summary import ProjectsAllocationsSummary
from domaindrivers.smartschedule.optimization.result import Result
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.smartschedule.simulation.simulated_capabilities import SimulatedCapabilities
from domaindrivers.smartschedule.simulation.simulation_facade import SimulationFacade


class PotentialTransfersService:
    __simulation_facade: Final[SimulationFacade]
    __cash_flow_facade: Final[CashFlowFacade]
    __project_allocations_repository: Final[ProjectAllocationsRepository]

    def __init__(
        self,
        simulation_facade: SimulationFacade,
        cash_flow_facade: CashFlowFacade,
        project_allocations_repository: ProjectAllocationsRepository,
    ):
        self.__simulation_facade = simulation_facade
        self.__cash_flow_facade = cash_flow_facade
        self.__project_allocations_repository = project_allocations_repository

    def profit_after_moving_capabilities(
        self, project_id: ProjectAllocationsId, capability_to_move: AllocatableCapabilitySummary, time_slot: TimeSlot
    ) -> float:
        # cached?
        potential_transfers: PotentialTransfers = PotentialTransfers(
            ProjectsAllocationsSummary.of(self.__project_allocations_repository.find_all()),
            self.__cash_flow_facade.find_all_earnings(),
        )
        return self.__check_potential_transfer(potential_transfers, project_id, capability_to_move, time_slot)

    def __check_potential_transfer(
        self,
        transfers: PotentialTransfers,
        project_to: ProjectAllocationsId,
        capability_to_move: AllocatableCapabilitySummary,
        for_slot: TimeSlot,
    ) -> float:
        result_before: Result = self.__simulation_facade.what_is_the_optimal_setup(
            transfers.to_simulated_projects(), SimulatedCapabilities.none()
        )
        transfers = transfers.transfer_project_to(project_to, capability_to_move, for_slot)
        result_after: Result = self.__simulation_facade.what_is_the_optimal_setup(
            transfers.to_simulated_projects(), SimulatedCapabilities.none()
        )
        return float(result_after.profit - result_before.profit)

    def check_potential_transfer(
        self,
        transfers: PotentialTransfers,
        project_from: ProjectAllocationsId,
        project_to: ProjectAllocationsId,
        capability: AllocatedCapability,
        for_slot: TimeSlot,
    ) -> float:
        result_before: Result = self.__simulation_facade.what_is_the_optimal_setup(
            transfers.to_simulated_projects(), SimulatedCapabilities.none()
        )
        transfers = transfers.transfer(project_from, project_to, capability, for_slot)
        result_after: Result = self.__simulation_facade.what_is_the_optimal_setup(
            transfers.to_simulated_projects(), SimulatedCapabilities.none()
        )
        return float(result_after.profit - result_before.profit)
