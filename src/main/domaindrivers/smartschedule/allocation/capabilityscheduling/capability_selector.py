from enum import Enum

from attr import frozen
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.utils.serializable import Serializable


@frozen
class CapabilitySelector(Serializable):
    class SelectingPolicy(Enum):
        ALL_SIMULTANEOUSLY = 0
        ONE_OF_ALL = 1

    capabilities: set[Capability]
    selecting_policy: SelectingPolicy

    @classmethod
    def can_perform_all_at_the_time(cls, capabilities: set[Capability]) -> "CapabilitySelector":
        return cls(capabilities, cls.SelectingPolicy.ALL_SIMULTANEOUSLY)

    @classmethod
    def can_perform_one_of(cls, capabilities: set[Capability]) -> "CapabilitySelector":
        return cls(capabilities, cls.SelectingPolicy.ONE_OF_ALL)

    def can_perform(self, capability: Capability) -> bool:
        return capability in self.capabilities

    def can_perform_capabilities(self, capabilities: set[Capability]) -> bool:
        if len(capabilities) == 1:
            return self.capabilities == capabilities
        return self.selecting_policy == self.SelectingPolicy.ALL_SIMULTANEOUSLY and self.capabilities == capabilities
