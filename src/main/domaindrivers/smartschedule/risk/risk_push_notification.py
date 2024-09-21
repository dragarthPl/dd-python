import domaindrivers.smartschedule.planning.demands
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capabilities_summary import (
    AllocatableCapabilitiesSummary,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.demand import Demand
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class RiskPushNotification:
    def notify_demands_satisfied(self, project_id: ProjectAllocationsId) -> None: ...

    def notify_about_availability(
        self, project_id: ProjectAllocationsId, available: dict[Demand, AllocatableCapabilitiesSummary]
    ) -> None: ...

    def notify_profitable_relocation_found(
        self, project_id: ProjectAllocationsId, allocatable_capability_id: AllocatableCapabilityId
    ) -> None: ...

    def notify_about_possible_risk(self, project_id: ProjectAllocationsId) -> None: ...

    def notify_about_possible_risk_during_planning(
        self, cause: ProjectId, demands: domaindrivers.smartschedule.planning.demands.Demands
    ) -> None: ...

    def notify_about_critical_resource_not_available(
        self, cause: ProjectId, critical_resource: ResourceId, time_slot: TimeSlot
    ) -> None: ...

    def notify_about_resources_not_available(self, project_id: ProjectId, not_available: set[ResourceId]) -> None: ...
