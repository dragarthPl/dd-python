from uuid import UUID

import domaindrivers.smartschedule.simulation.demand
import domaindrivers.smartschedule.simulation.demands
from attr import frozen
from domaindrivers.smartschedule.allocation.allocated_capability import AllocatedCapability
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project import Project
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.smartschedule.simulation.project_id import ProjectId
from domaindrivers.smartschedule.simulation.simulated_project import SimulatedProject


@frozen
class Projects:
    projects: dict[UUID, Project]

    def transfer(
        self, project_from_id: UUID, project_to_id: UUID, capability: AllocatedCapability, for_slot: TimeSlot
    ) -> "Projects":
        project_from: Project = self.projects.get(project_from_id)
        project_to = self.projects.get(project_to_id)
        if not project_from or not project_to:
            return self
        removed: AllocatedCapability = project_from.remove(capability, for_slot)
        if not removed:
            return self
        project_to.add(AllocatedCapability.of(removed.resource_id, removed.capability, for_slot))
        return Projects(self.projects)

    def to_simulated_projects(self) -> list[SimulatedProject]:
        return list(
            map(
                lambda entry: SimulatedProject(
                    ProjectId.from_key(entry[0]), lambda: entry[1].earnings, self.get_missing_demands(entry[1])
                ),
                self.projects.items(),
            )
        )

    def get_missing_demands(self, project: Project) -> domaindrivers.smartschedule.simulation.demands.Demands:
        all_demands: Demands = project.missing_demands()
        return domaindrivers.smartschedule.simulation.demands.Demands(
            list(
                map(
                    lambda demand: domaindrivers.smartschedule.simulation.demand.Demand(demand.capability, demand.slot),
                    all_demands.all,
                )
            )
        )
