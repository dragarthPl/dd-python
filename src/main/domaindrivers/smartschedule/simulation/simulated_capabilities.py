from attrs import frozen
from domaindrivers.smartschedule.simulation.available_resource_capability import AvailableResourceCapability


@frozen
class SimulatedCapabilities:
    capabilities: list[AvailableResourceCapability]

    @classmethod
    def none(cls) -> "SimulatedCapabilities":
        return cls([])

    def __is_list_of_available_resource_capability(self, new_capabilities: list[AvailableResourceCapability]) -> bool:
        if not isinstance(new_capabilities, list):
            return False
        for capability in new_capabilities:
            if not isinstance(capability, AvailableResourceCapability):
                return False
        return True

    def add(
        self, new_capabilities: list[AvailableResourceCapability] | AvailableResourceCapability
    ) -> "SimulatedCapabilities":
        new_availabilities = self.capabilities[:]
        if isinstance(new_capabilities, AvailableResourceCapability):
            new_availabilities.append(new_capabilities)
        elif self.__is_list_of_available_resource_capability(new_capabilities):
            new_availabilities.extend(new_capabilities)
        else:
            raise Exception("Invalid type, must be AvailableResourceCapability or list[AvailableResourceCapability]")
        return SimulatedCapabilities(new_availabilities)
