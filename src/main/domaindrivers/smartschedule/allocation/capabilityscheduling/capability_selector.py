from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.utils.serializable import Serializable


class CapabilitySelector(Serializable):
    @staticmethod
    def can_perform_one_of(capabilities: set[Capability]) -> "CapabilitySelector":
        return None

    @staticmethod
    def can_perform_all_at_the_time(being_an_admin: set[Capability]) -> "CapabilitySelector":
        return None

    def can_perform(self, capability: Capability) -> bool:
        return False

    def can_perform_capabilities(self, capabilities: set[Capability]) -> bool:
        return False
