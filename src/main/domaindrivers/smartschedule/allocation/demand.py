from attr import frozen
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class Demand:
    capability: Capability
    slot: TimeSlot
