from attr import frozen
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_summary import (
    AllocatableCapabilitySummary,
)


@frozen
class AllocatableCapabilitiesSummary:
    all: list[AllocatableCapabilitySummary]
