from uuid import UUID

from domaindrivers.smartschedule.shared.time_slot import TimeSlot
from domaindrivers.smartschedule.simulation.available_resource_capability import AvailableResourceCapability
from domaindrivers.smartschedule.simulation.capability import Capability
from domaindrivers.smartschedule.simulation.simulated_capabilities import SimulatedCapabilities


class AvailableCapabilitiesBuilder:
    __availabilities: list[AvailableResourceCapability]
    __current_resource_id: UUID
    __capability: Capability
    __time_slot: TimeSlot

    def __init__(self) -> None:
        self.__availabilities = []
        self.__current_resource_id = None
        self.__capability = None
        self.__time_slot = None

    def with_employee(self, current_resource_id: UUID) -> "AvailableCapabilitiesBuilder":
        if self.__current_resource_id:
            self.__availabilities.append(
                AvailableResourceCapability(self.__current_resource_id, self.__capability, self.__time_slot)
            )
        self.__current_resource_id = current_resource_id
        return self

    def that_brings(self, capability: Capability) -> "AvailableCapabilitiesBuilder":
        self.__capability = capability
        return self

    def that_is_available_at(self, time_slot: TimeSlot) -> "AvailableCapabilitiesBuilder":
        self.__time_slot = time_slot
        return self

    def build(self) -> SimulatedCapabilities:
        if self.__current_resource_id:
            self.__availabilities.append(
                AvailableResourceCapability(self.__current_resource_id, self.__capability, self.__time_slot)
            )
        return SimulatedCapabilities(self.__availabilities)
