from domaindrivers.smartschedule.simulation.available_resource_capability import AvailableResourceCapability
from domaindrivers.smartschedule.simulation.demands import Demands
from domaindrivers.smartschedule.simulation.result import Result
from domaindrivers.smartschedule.simulation.simulated_capabilities import SimulatedCapabilities
from domaindrivers.smartschedule.simulation.simulated_project import SimulatedProject


class SimulationFacade:
    def which_project_with_missing_demands_is_most_profitable_to_allocate_resources_to(
        self,
        projects_simulations: list[SimulatedProject],
        total_capability: SimulatedCapabilities,
    ) -> Result:
        available_resource_capability_list: list[AvailableResourceCapability] = total_capability.capabilities
        capacities_size: int = len(available_resource_capability_list)
        dp: list[float] = [0.0 for _ in range(capacities_size + 1)]
        chosen_items_list: list[list[SimulatedProject]] = []
        allocated_capacities_list: list[set[AvailableResourceCapability]] = []

        automatically_included_items: list[SimulatedProject] = list(
            filter(lambda x: x.all_demands_satisfied(), projects_simulations)
        )
        guaranteed_value: float = sum(map(lambda x: float(x.earnings), automatically_included_items))

        for i in range(capacities_size + 1):
            chosen_items_list.append([])
            allocated_capacities_list.append(set())

        all_availabilities: list[AvailableResourceCapability] = available_resource_capability_list.copy()
        item_to_capacities_map: dict[SimulatedProject, set[AvailableResourceCapability]] = {}

        for project in sorted(projects_simulations, key=lambda x: x.earnings, reverse=True):
            chosen_capacities: list[AvailableResourceCapability] = self.match_capacities(
                project.missing_demands,
                all_availabilities,
            )
            all_availabilities = list(filter(lambda a: a not in chosen_capacities, all_availabilities))

            if not chosen_capacities:
                continue

            sum_value: float = float(project.earnings)
            chosen_capacities_count: int = len(chosen_capacities)

            for j in range(capacities_size, chosen_capacities_count - 1, -1):
                if dp[j] < sum_value + dp[j - chosen_capacities_count]:
                    dp[j] = sum_value + dp[j - chosen_capacities_count]

                    chosen_items_list[j] = chosen_items_list[j - chosen_capacities_count].copy()
                    chosen_items_list[j].append(project)

                    allocated_capacities_list[j].clear()
                    allocated_capacities_list[j].update(chosen_capacities)

            item_to_capacities_map[project] = set(chosen_capacities)

        chosen_items_list[capacities_size].extend(automatically_included_items)
        return Result(
            dp[capacities_size] + float(guaranteed_value), chosen_items_list[capacities_size], item_to_capacities_map
        )

    def match_capacities(
        self, demands: Demands, available_capacities: list[AvailableResourceCapability]
    ) -> list[AvailableResourceCapability]:
        result: list[AvailableResourceCapability] = []
        for single_demand in demands.all:
            matching_capacity: AvailableResourceCapability = next(
                filter(single_demand.is_satisfied_by, available_capacities), None
            )

            if matching_capacity:
                result.append(matching_capacity)
            else:
                return []
        return result
