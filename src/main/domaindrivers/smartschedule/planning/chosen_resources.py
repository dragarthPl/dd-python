from attr import frozen
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class ChosenResources:
    resources: set[ResourceId]
    time_slot: TimeSlot

    @classmethod
    def none(cls) -> "ChosenResources":
        return cls(set(), TimeSlot.empty())
