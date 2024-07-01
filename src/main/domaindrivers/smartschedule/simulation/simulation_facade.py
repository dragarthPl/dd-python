from domaindrivers.smartschedule.simulation.result import Result
from domaindrivers.smartschedule.simulation.simulated_capabilities import SimulatedCapabilities
from domaindrivers.smartschedule.simulation.simulated_project import SimulatedProject


class SimulationFacade:
    def which_project_with_missing_demands_is_most_profitable_to_allocate_resources_to(
        self,
        projects: list[SimulatedProject],
        totalCapability: SimulatedCapabilities,
    ) -> Result:
        return Result(0.0, [], {})
