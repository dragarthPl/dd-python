import domaindrivers.smartschedule.simulation.demand
import domaindrivers.smartschedule.simulation.demands
from attr import frozen
from domaindrivers.smartschedule.allocation.allocated_capability import AllocatedCapability
from domaindrivers.smartschedule.allocation.allocations import Allocations
from domaindrivers.smartschedule.allocation.cashflow.earnings import Earnings
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.allocation.projects_allocations_summary import ProjectsAllocationsSummary
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.smartschedule.simulation.project_id import ProjectId
from domaindrivers.smartschedule.simulation.simulated_project import SimulatedProject


@frozen
class PotentialTransfers:
    summary: ProjectsAllocationsSummary
    earnings: dict[ProjectAllocationsId, Earnings]

    def transfer(
        self,
        project_from: ProjectAllocationsId,
        project_to: ProjectAllocationsId,
        allocated_capability: AllocatedCapability,
        for_slot: TimeSlot,
    ) -> "PotentialTransfers":
        from_project: Allocations = self.summary.project_allocations.get(project_from)
        to_project: Allocations = self.summary.project_allocations.get(project_to)
        if not from_project or not to_project:
            return self
        new_allocations_project_from: Allocations = from_project.remove(
            allocated_capability.allocated_capability_id, for_slot
        )
        if new_allocations_project_from == from_project:
            return self
        self.summary.project_allocations[project_from] = new_allocations_project_from
        new_allocations_project_to: Allocations = to_project.add(
            AllocatedCapability(allocated_capability.allocated_capability_id, allocated_capability.capability, for_slot)
        )
        self.summary.project_allocations[project_to] = new_allocations_project_to
        return PotentialTransfers(self.summary, self.earnings)

    def to_simulated_projects(self) -> list[SimulatedProject]:
        return list(
            map(
                lambda project: SimulatedProject(
                    ProjectId.from_key(project.id()),
                    lambda: self.earnings[project].to_decimal(),
                    self.get_missing_demands(project),
                ),
                self.summary.project_allocations.keys(),
            )
        )

    def get_missing_demands(
        self, project_allocations_id: ProjectAllocationsId
    ) -> domaindrivers.smartschedule.simulation.demands.Demands:
        all_demands: Demands = self.summary.demands[project_allocations_id].missing_demands(
            self.summary.project_allocations[project_allocations_id]
        )
        return domaindrivers.smartschedule.simulation.demands.Demands(
            list(
                map(
                    lambda demand: domaindrivers.smartschedule.simulation.demand.Demand(demand.capability, demand.slot),
                    all_demands.all,
                )
            )
        )
