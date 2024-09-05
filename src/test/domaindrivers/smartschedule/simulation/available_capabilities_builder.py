from uuid import UUID

from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.capability_selector import CapabilitySelector
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.smartschedule.simulation.available_resource_capability import AvailableResourceCapability
from domaindrivers.smartschedule.simulation.simulated_capabilities import SimulatedCapabilities


class AvailableCapabilitiesBuilder:
    __availabilities: list[AvailableResourceCapability]
    __current_resource_id: UUID
    __capabilities: set[Capability]
    __time_slot: TimeSlot
    __selecting_policy: CapabilitySelector.SelectingPolicy

    def __init__(self) -> None:
        self.__availabilities = []
        self.__current_resource_id = None
        self.__capability = None
        self.__time_slot = None

    def with_employee(self, current_resource_id: UUID) -> "AvailableCapabilitiesBuilder":
        if self.__current_resource_id:
            self.__availabilities.append(
                AvailableResourceCapability(
                    self.__current_resource_id,
                    CapabilitySelector(self.__capabilities, self.__selecting_policy),
                    self.__time_slot,
                )
            )
        self.__current_resource_id = current_resource_id
        return self

    def that_brings(self, capability: Capability) -> "AvailableCapabilitiesBuilder":
        self.__capabilities = {capability}
        self.__selecting_policy = CapabilitySelector.SelectingPolicy.ONE_OF_ALL
        return self

    def that_is_available_at(self, time_slot: TimeSlot) -> "AvailableCapabilitiesBuilder":
        self.__time_slot = time_slot
        return self

    def build(self) -> SimulatedCapabilities:
        if self.__current_resource_id:
            self.__availabilities.append(
                AvailableResourceCapability(
                    self.__current_resource_id,
                    CapabilitySelector(self.__capabilities, self.__selecting_policy),
                    time_slot=self.__time_slot,
                )
            )
        return SimulatedCapabilities(self.__availabilities)

    def that_brings_simultaneously(self, *skills: Capability) -> "AvailableCapabilitiesBuilder":
        self.__capabilities = set(skills)
        self.__selecting_policy = CapabilitySelector.SelectingPolicy.ALL_SIMULTANEOUSLY
        return self
