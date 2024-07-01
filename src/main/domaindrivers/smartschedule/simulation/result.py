from typing import override

from attrs import frozen
from domaindrivers.smartschedule.simulation.available_resource_capability import AvailableResourceCapability
from domaindrivers.smartschedule.simulation.simulated_project import SimulatedProject


@frozen
class Result:
    profit: float
    chosen_projects: list[SimulatedProject]
    resources_allocated_to_projects: dict[SimulatedProject, set[AvailableResourceCapability]]

    def to_string(self) -> str:
        return f"Result{{profit={self.profit} , items={self.chosen_projects}}}"

    @override
    def __str__(self) -> str:
        return self.to_string()
