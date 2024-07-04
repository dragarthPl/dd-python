from attr import frozen
from domaindrivers.smartschedule.optimization.capacity_dimension import CapacityDimension


@frozen
class TotalCapacity:
    capacities: list[CapacityDimension]

    @classmethod
    def of(cls, *capacities: CapacityDimension) -> "TotalCapacity":
        return cls(list(capacities))

    @classmethod
    def of_list(cls, capacities: list[CapacityDimension]) -> "TotalCapacity":
        return cls(capacities)

    @classmethod
    def zero(cls) -> "TotalCapacity":
        return cls([])

    def size(self) -> int:
        return len(self.capacities)

    def add(self, capacities: list[CapacityDimension]) -> "TotalCapacity":
        new_capacities: list[CapacityDimension] = self.capacities + capacities
        return TotalCapacity.of_list(new_capacities)
