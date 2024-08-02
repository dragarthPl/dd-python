from attr import frozen
from domaindrivers.smartschedule.shared.resource_name import ResourceName
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class ChosenResources:
    resources: set[ResourceName]
    time_slot: TimeSlot

    @classmethod
    def none(cls) -> "ChosenResources":
        return cls(set(), None)
