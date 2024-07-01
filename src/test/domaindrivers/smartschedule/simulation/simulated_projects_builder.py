from __future__ import annotations

from decimal import Decimal

from domaindrivers.smartschedule.simulation.demand import Demand
from domaindrivers.smartschedule.simulation.demands import Demands
from domaindrivers.smartschedule.simulation.project_id import ProjectId
from domaindrivers.smartschedule.simulation.simulated_project import SimulatedProject


class SimulatedProjectsBuilder:
    __current_id: ProjectId
    __simulated_projects: list[ProjectId]
    __simulated_demands: dict[ProjectId, Demands]
    __simulated_earnings: dict[ProjectId, Decimal]

    def __init__(self) -> None:
        self.__current_id = None
        self.__simulated_projects = []
        self.__simulated_demands = {}
        self.__simulated_earnings = {}

    def with_project(self, project_id: ProjectId) -> "SimulatedProjectsBuilder":
        self.__current_id = project_id
        self.__simulated_projects.append(project_id)
        return self

    def that_requires(self, *demands: Demand) -> "SimulatedProjectsBuilder":
        self.__simulated_demands[self.__current_id] = Demands.of(*demands)
        return self

    def that_can_earn(self, earnings: Decimal) -> "SimulatedProjectsBuilder":
        self.__simulated_earnings[self.__current_id] = earnings
        return self

    def build(self) -> list[SimulatedProject]:
        return list(
            map(
                lambda some_id: SimulatedProject(
                    some_id, self.__simulated_earnings.get(some_id), self.__simulated_demands.get(some_id)
                ),
                self.__simulated_projects,
            )
        )
