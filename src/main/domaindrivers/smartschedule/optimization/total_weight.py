from typing import Any

from attr import frozen
from domaindrivers.smartschedule.optimization.weight_dimension import WeightDimension


@frozen
class TotalWeight:
    components: list[WeightDimension[Any]]

    @classmethod
    def zero(cls) -> "TotalWeight":
        return cls([])

    @classmethod
    def of(cls, *components: WeightDimension[Any]) -> "TotalWeight":
        return cls(list(components))
