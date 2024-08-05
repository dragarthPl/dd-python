from uuid import UUID

from attr import frozen
from domaindrivers.smartschedule.allocation.allocated_capability import AllocatedCapability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


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

    def remove(self, to_remove: UUID, slot: TimeSlot) -> "Allocations":
        return next(map(lambda ar: self.__remove_from_slot(ar, slot), filter(bool, [self.find(to_remove)])), self)

    def __remove_from_slot(self, allocated_resource: AllocatedCapability, slot: TimeSlot) -> "Allocations":
        left_overs: set[AllocatedCapability] = set(
            map(
                lambda left_over: AllocatedCapability.of(
                    allocated_resource.resource_id, allocated_resource.capability, left_over
                ),
                filter(
                    lambda left_over: left_over.within(allocated_resource.time_slot),
                    allocated_resource.time_slot.leftover_after_removing_common_with(slot),
                ),
            )
        )
        new_slots: set[AllocatedCapability] = set(self.all)
        new_slots.remove(allocated_resource)
        for el in left_overs:
            new_slots.add(el)
        return Allocations(new_slots)

    def find(self, allocated_capability_id: UUID) -> AllocatedCapability:
        return next(filter(lambda ar: ar.allocated_capability_id == allocated_capability_id, self.all), None)
