from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from domaindrivers.smartschedule.optimization.capacity_dimension import CapacityDimension

T = TypeVar("T", bound=CapacityDimension)


class WeightDimension(ABC, Generic[T]):
    @abstractmethod
    def is_satisfied_by(self, capacity_dimension: T) -> bool:
        pass
