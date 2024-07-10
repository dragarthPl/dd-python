from typing import Final
from uuid import UUID

from domaindrivers.smartschedule.allocation.allocated_capability import AllocatedCapability
from domaindrivers.smartschedule.allocation.projects import Projects
from domaindrivers.smartschedule.optimization.result import Result
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.smartschedule.simulation.simulated_capabilities import SimulatedCapabilities
from domaindrivers.smartschedule.simulation.simulation_facade import SimulationFacade


class AllocationFacade:
    __simulation_facade: Final[SimulationFacade]

    def __init__(self, simulation_facade: SimulationFacade):
        self.__simulation_facade = simulation_facade

    def check_potential_transfer(
        self,
        projects: Projects,
        project_from: UUID,
        project_to: UUID,
        capability: AllocatedCapability,
        for_slot: TimeSlot,
    ) -> float:
        # Project rather fetched from db.
        result_before: Result = self.__simulation_facade.what_is_the_optimal_setup(
            projects.to_simulated_projects(), SimulatedCapabilities.none()
        )
        projects = projects.transfer(project_from, project_to, capability, for_slot)
        result_after: Result = self.__simulation_facade.what_is_the_optimal_setup(
            projects.to_simulated_projects(), SimulatedCapabilities.none()
        )
        return float(result_after.profit - result_before.profit)
