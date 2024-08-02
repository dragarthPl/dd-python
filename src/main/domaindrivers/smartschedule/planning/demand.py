from attr import frozen
from domaindrivers.smartschedule.shared.capability.capability import Capability


@frozen
class Demand:
    capability: Capability

    @classmethod
    def demand_for(cls, capability: Capability) -> "Demand":
        return cls(capability)
