from typing import override

from attrs import frozen
from domaindrivers.smartschedule.optimization.capacity_dimension import CapacityDimension
from domaindrivers.smartschedule.optimization.item import Item


@frozen
class Result:
    profit: float
    chosen_items: list[Item]
    item_to_capacities: dict[Item, set[CapacityDimension]]

    def to_string(self) -> str:
        return f"Result{{profit={self.profit} , chosenItems={self.chosen_items}}}"

    @override
    def __str__(self) -> str:
        return self.to_string()
