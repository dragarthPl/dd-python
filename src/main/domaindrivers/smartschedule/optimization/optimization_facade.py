import functools
from typing import Callable

from domaindrivers.smartschedule.optimization.capacity_dimension import CapacityDimension
from domaindrivers.smartschedule.optimization.item import Item
from domaindrivers.smartschedule.optimization.result import Result
from domaindrivers.smartschedule.optimization.total_capacity import TotalCapacity
from domaindrivers.smartschedule.optimization.total_weight import TotalWeight


class OptimizationFacade:
    def calculate(self, items: list[Item], total_capacity: TotalCapacity) -> Result:
        def comparator(x: Item, y: Item) -> int:
            return int(y.value - x.value)

        return self.calculate_with_comparator(items, total_capacity, comparator)

    def calculate_with_comparator(
        self, items: list[Item], total_capacity: TotalCapacity, comparator: Callable[[Item, Item], int]
    ) -> Result:
        capacities_size: int = total_capacity.size()
        dp: list[float] = [0.0 for _ in range(capacities_size + 1)]
        chosen_items_list: list[list[Item]] = []
        allocated_capacities_list: list[set[CapacityDimension]] = []

        automatically_included_items: list[Item] = list(filter(lambda item: item.is_weight_zero(), items))
        guaranteed_value: float = sum(map(lambda item: item.value, automatically_included_items))

        for _ in range(capacities_size + 1):
            chosen_items_list.append([])
            allocated_capacities_list.append(set())

        all_capacities: list[CapacityDimension] = total_capacity.capacities
        item_to_capacities_map: dict[Item, set[CapacityDimension]] = {}

        for item in sorted(items, key=functools.cmp_to_key(comparator)):
            chosen_capacities: list[CapacityDimension] = self.__match_capacities(item.total_weight, all_capacities)
            all_capacities = list(filter(lambda a: a not in chosen_capacities, all_capacities))

            if not chosen_capacities:
                continue

            sum_value: float = item.value
            chosen_capacities_count: int = len(chosen_capacities)

            for j in range(capacities_size, chosen_capacities_count - 1, -1):
                if dp[j] < dp[j - chosen_capacities_count] + sum_value:
                    dp[j] = dp[j - chosen_capacities_count] + sum_value

                    chosen_items_list[j] = chosen_items_list[j - chosen_capacities_count].copy()
                    chosen_items_list[j].append(item)

                    allocated_capacities_list[j].union(chosen_capacities)
            item_to_capacities_map[item] = set(chosen_capacities)

        chosen_items_list[capacities_size].extend(automatically_included_items)
        return Result(
            dp[capacities_size] + guaranteed_value, chosen_items_list[capacities_size], item_to_capacities_map
        )

    def __match_capacities(
        self, total_weight: TotalWeight, available_capacities: list[CapacityDimension]
    ) -> list[CapacityDimension]:
        result: list[CapacityDimension] = []
        for weight_component in total_weight.components:
            matching_capacity: CapacityDimension = next(
                filter(lambda x: weight_component.is_satisfied_by(x), available_capacities), None
            )

            if matching_capacity:
                result.append(matching_capacity)
            else:
                return []
        return result
