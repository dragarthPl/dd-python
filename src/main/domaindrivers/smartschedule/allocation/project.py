from decimal import Decimal

from domaindrivers.smartschedule.allocation.allocated_capability import AllocatedCapability
from domaindrivers.smartschedule.allocation.allocations import Allocations
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class Project:
    __earnings: Decimal
    __demands: Demands
    __allocations: Allocations

    def __init__(self, demands: Demands, earnings: Decimal) -> None:
        self.__earnings = earnings
        self.__demands = demands
        self.__allocations = Allocations.none()

    def missing_demands(self) -> Demands:
        return self.__demands.missing_demands(self.__allocations)

    @property
    def earnings(self) -> Decimal:
        return self.__earnings

    def remove(self, capability: AllocatedCapability, for_slot: TimeSlot) -> AllocatedCapability:
        to_remove: AllocatedCapability = self.__allocations.find(capability.allocated_capability_id)
        if not to_remove:
            return None
        self.__allocations = self.__allocations.remove(capability.allocated_capability_id, for_slot)
        return to_remove

    def add(self, allocated_capability: AllocatedCapability) -> Allocations:
        self.__allocations = self.__allocations.add(allocated_capability)
        return self.__allocations
