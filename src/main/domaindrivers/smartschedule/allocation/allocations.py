from attr import frozen
from domaindrivers.smartschedule.allocation.allocated_capability import AllocatedCapability
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.utils.optional import Optional


@frozen
class Allocations:
    all: set[AllocatedCapability]

    @staticmethod
    def none() -> "Allocations":
        return Allocations(set())

    def add(self, new_capability: AllocatedCapability) -> "Allocations":
        all: set[AllocatedCapability] = self.all.copy()
        all.add(new_capability)
        return Allocations(all)

    def remove(self, to_remove: AllocatableCapabilityId, slot: TimeSlot) -> "Allocations":
        return self.find(to_remove).map(lambda ar: self.__remove_from_slot(ar, slot)).or_else(self)

    def __remove_from_slot(self, allocated_capability: AllocatedCapability, slot: TimeSlot) -> "Allocations":
        left_overs: set[AllocatedCapability] = set(
            map(
                lambda left_over: AllocatedCapability(
                    allocated_capability.allocated_capability_id, allocated_capability.capability, left_over
                ),
                filter(
                    lambda left_over: left_over.within(allocated_capability.time_slot),
                    allocated_capability.time_slot.leftover_after_removing_common_with(slot),
                ),
            )
        )
        new_slots: set[AllocatedCapability] = set(self.all)
        new_slots.remove(allocated_capability)
        for el in left_overs:
            new_slots.add(el)
        return Allocations(new_slots)

    def find(self, allocated_capability_id: AllocatableCapabilityId) -> Optional[AllocatedCapability]:
        return Optional(next(filter(lambda ar: ar.allocated_capability_id == allocated_capability_id, self.all), None))
