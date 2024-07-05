from typing import Any, cast

from domaindrivers.smartschedule.optimization.capacity_dimension import CapacityDimension
from domaindrivers.smartschedule.optimization.item import Item
from domaindrivers.smartschedule.optimization.optimization_facade import OptimizationFacade
from domaindrivers.smartschedule.optimization.result import Result
from domaindrivers.smartschedule.optimization.total_capacity import TotalCapacity
from domaindrivers.smartschedule.optimization.total_weight import TotalWeight
from domaindrivers.smartschedule.optimization.weight_dimension import WeightDimension
from domaindrivers.smartschedule.simulation.available_resource_capability import AvailableResourceCapability
from domaindrivers.smartschedule.simulation.demand import Demand
from domaindrivers.smartschedule.simulation.simulated_capabilities import SimulatedCapabilities
from domaindrivers.smartschedule.simulation.simulated_project import SimulatedProject


class SimulationFacade:
    __optimization_facade: OptimizationFacade

    def __init__(self, optimization_facade: OptimizationFacade) -> None:
        self.__optimization_facade = optimization_facade

    def which_project_with_missing_demands_is_most_profitable_to_allocate_resources_to(
        self,
        projects_simulations: list[SimulatedProject],
        total_capability: SimulatedCapabilities,
    ) -> Result:
        return self.__optimization_facade.calculate(
            self.__to_items(projects_simulations), self.__to_capacity(total_capability)
        )

    def __to_capacity(self, simulated_capabilities: SimulatedCapabilities) -> TotalCapacity:
        capabilities: list[AvailableResourceCapability] = simulated_capabilities.capabilities
        capacity_dimensions: list[CapacityDimension] = cast(list[CapacityDimension], capabilities.copy())
        return TotalCapacity(capacity_dimensions)

    def __to_items(self, projects_simulations: list[SimulatedProject]) -> list[Item]:
        return list(map(lambda simulation: self.__to_item(simulation), projects_simulations))

    def __to_item(self, simulated_project: SimulatedProject) -> Item:
        missing_demands: list[Demand] = simulated_project.missing_demands.all
        weights: list[WeightDimension[Any]] = cast(list[WeightDimension[Any]], missing_demands.copy())
        return Item(str(simulated_project.project_id), float(simulated_project.calculate_value()), TotalWeight(weights))
