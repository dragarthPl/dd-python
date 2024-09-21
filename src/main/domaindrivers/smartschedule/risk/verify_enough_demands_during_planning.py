import uuid
from decimal import Decimal
from typing import Final

from domaindrivers.smartschedule.optimization.result import Result
from domaindrivers.smartschedule.planning.capabilities_demanded import CapabilitiesDemanded
from domaindrivers.smartschedule.planning.planning_facade import PlanningFacade
from domaindrivers.smartschedule.planning.project_card import ProjectCard
from domaindrivers.smartschedule.resource.resource_facade import ResourceFacade
from domaindrivers.smartschedule.risk.risk_push_notification import RiskPushNotification
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.capability_selector import CapabilitySelector
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.smartschedule.simulation.available_resource_capability import AvailableResourceCapability
from domaindrivers.smartschedule.simulation.demand import Demand
from domaindrivers.smartschedule.simulation.demands import Demands
from domaindrivers.smartschedule.simulation.project_id import ProjectId
from domaindrivers.smartschedule.simulation.simulated_capabilities import SimulatedCapabilities
from domaindrivers.smartschedule.simulation.simulated_project import SimulatedProject
from domaindrivers.smartschedule.simulation.simulation_facade import SimulationFacade


class VerifyEnoughDemandsDuringPlanning:
    SAME_ARBITRARY_VALUE_FOR_EVERY_PROJECT: Final[int] = 100

    __planning_facade: PlanningFacade
    __simulation_facade: SimulationFacade
    __resource_facade: ResourceFacade
    __risk_push_notification: RiskPushNotification

    def __init__(
        self,
        planning_facade: PlanningFacade,
        simulation_facade: SimulationFacade,
        resource_facade: ResourceFacade,
        risk_push_notification: RiskPushNotification,
    ) -> None:
        self.__planning_facade = planning_facade
        self.__simulation_facade = simulation_facade
        self.__resource_facade = resource_facade
        self.__risk_push_notification = risk_push_notification

    # @EventListener
    def handle(self, capabilities_demanded: CapabilitiesDemanded) -> None:
        project_summaries: list[ProjectCard] = self.__planning_facade.load_all()
        all_capabilities: list[Capability] = self.__resource_facade.find_all_capabilities()
        if self.__not_able_to_handle_all_projects_given_capabilities(project_summaries, all_capabilities):
            self.__risk_push_notification.notify_about_possible_risk_during_planning(
                capabilities_demanded.project_id, capabilities_demanded.demands
            )

    def __not_able_to_handle_all_projects_given_capabilities(
        self, project_summaries: list[ProjectCard], all_capabilities: list[Capability]
    ) -> bool:
        capabilities: list[AvailableResourceCapability] = list(
            map(
                lambda cap: AvailableResourceCapability(
                    uuid.uuid4(), CapabilitySelector.can_just_perform(cap), TimeSlot.empty()
                ),
                all_capabilities,
            )
        )
        simulated_projects: list[SimulatedProject] = list(
            map(self.__create_same_price_simulated_project, project_summaries)
        )
        result: Result = self.__simulation_facade.what_is_the_optimal_setup(
            simulated_projects, SimulatedCapabilities(capabilities)
        )
        return len(result.chosen_items) != len(project_summaries)

    def __create_same_price_simulated_project(self, card: ProjectCard) -> SimulatedProject:
        simulated_demands: list[Demand] = list(
            map(lambda demand: Demand(demand.capability, TimeSlot.empty()), card.demands.all)
        )
        return SimulatedProject(
            ProjectId.from_key(card.project_id.id()),
            lambda: Decimal(self.SAME_ARBITRARY_VALUE_FOR_EVERY_PROJECT),
            Demands(simulated_demands),
        )
