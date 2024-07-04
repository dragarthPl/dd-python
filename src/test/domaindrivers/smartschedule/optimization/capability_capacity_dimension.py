from typing import override
from uuid import UUID, uuid4

from attr import frozen
from domaindrivers.smartschedule.optimization.capacity_dimension import CapacityDimension
from domaindrivers.smartschedule.optimization.weight_dimension import WeightDimension
from domaindrivers.smartschedule.shared.time_slot import TimeSlot


@frozen
class CapabilityCapacityDimension(CapacityDimension):
    uuid: UUID
    id: str
    capacity_name: str
    capacity_type: str

    def of_random_uuid(self, id: str, capacity_name: str, capacity_type: str) -> "CapabilityCapacityDimension":
        return CapabilityCapacityDimension(uuid4(), id, capacity_name, capacity_type)


@frozen
class CapabilityWeightDimension(WeightDimension[CapabilityCapacityDimension]):
    name: str
    capability_type: str

    @override
    def is_satisfied_by(self, capacity_dimension: CapabilityCapacityDimension) -> bool:
        return (
            capacity_dimension.capacity_name == self.name and capacity_dimension.capacity_type == self.capability_type
        )


@frozen
class CapabilityTimedCapacityDimension(CapacityDimension):
    uuid: UUID
    id: str
    capacity_name: str
    capacity_type: str
    time_slot: TimeSlot

    @classmethod
    def of_random_uuid(
        cls, id: str, capacity_name: str, capacity_type: str, time_slot: TimeSlot
    ) -> "CapabilityTimedCapacityDimension":
        return cls(uuid4(), id, capacity_name, capacity_type, time_slot)


@frozen
class CapabilityTimedWeightDimension(WeightDimension[CapabilityTimedCapacityDimension]):
    name: str
    capability_type: str
    time_slot: TimeSlot

    @override
    def is_satisfied_by(self, capacity_timed_dimension: CapabilityTimedCapacityDimension) -> bool:
        return (
            capacity_timed_dimension.capacity_name == self.name
            and capacity_timed_dimension.capacity_type == self.capability_type
            and self.time_slot.within(capacity_timed_dimension.time_slot)
        )
