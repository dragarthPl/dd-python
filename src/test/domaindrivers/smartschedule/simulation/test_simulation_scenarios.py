import uuid
from decimal import Decimal
from unittest import TestCase
from uuid import UUID

from domaindrivers.smartschedule.simulation.available_resource_capability import AvailableResourceCapability
from domaindrivers.smartschedule.simulation.capability import Capability
from domaindrivers.smartschedule.simulation.demand import Demand
from domaindrivers.smartschedule.simulation.project_id import ProjectId
from domaindrivers.smartschedule.simulation.result import Result
from domaindrivers.smartschedule.simulation.simulated_capabilities import SimulatedCapabilities
from domaindrivers.smartschedule.simulation.simulated_project import SimulatedProject
from domaindrivers.smartschedule.simulation.simulation_facade import SimulationFacade
from domaindrivers.smartschedule.simulation.time_slot import TimeSlot

from .available_capabilities_builder import AvailableCapabilitiesBuilder
from .simulated_projects_builder import SimulatedProjectsBuilder


class TestSimulationScenarios(TestCase):
    JAN_1: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
    PROJECT_1: ProjectId = ProjectId.new_one()
    PROJECT_2: ProjectId = ProjectId.new_one()
    PROJECT_3: ProjectId = ProjectId.new_one()
    STASZEK: UUID = uuid.uuid4()
    LEON: UUID = uuid.uuid4()

    simulation_facade: SimulationFacade = SimulationFacade()

    def test_picks_optimal_project_based_on_earnings(self) -> None:
        # given
        simulated_projects: list[SimulatedProject] = (
            self.simulated_projects()
            .with_project(self.PROJECT_1)
            .that_requires(Demand.demand_for(Capability.skill("JAVA-MID"), self.JAN_1))
            .that_can_earn(Decimal(9))
            .with_project(self.PROJECT_2)
            .that_requires(Demand.demand_for(Capability.skill("JAVA-MID"), self.JAN_1))
            .that_can_earn(Decimal(99))
            .with_project(self.PROJECT_3)
            .that_requires(Demand.demand_for(Capability.skill("JAVA-MID"), self.JAN_1))
            .that_can_earn(Decimal(2))
            .build()
        )

        # and there are
        simulated_availability: SimulatedCapabilities = (
            self.simulated_capabilities()
            .with_employee(self.STASZEK)
            .that_brings(Capability.skill("JAVA-MID"))
            .that_is_available_at(self.JAN_1)
            .with_employee(self.LEON)
            .that_brings(Capability.skill("JAVA-MID"))
            .that_is_available_at(self.JAN_1)
            .build()
        )

        # when
        result: Result = (
            self.simulation_facade.which_project_with_missing_demands_is_most_profitable_to_allocate_resources_to(
                simulated_projects, simulated_availability
            )
        )

        # then
        self.assertEqual(108.0, result.profit)
        self.assertEqual(2, len(result.chosen_projects))

    def test_picks_all_when_enough_capabilities(self) -> None:
        # given
        simulated_projects: list[SimulatedProject] = (
            self.simulated_projects()
            .with_project(self.PROJECT_1)
            .that_requires(Demand.demand_for(Capability.skill("JAVA-MID"), self.JAN_1))
            .that_can_earn(Decimal(99))
            .build()
        )

        # and there are
        simulated_availability: SimulatedCapabilities = (
            self.simulated_capabilities()
            .with_employee(self.STASZEK)
            .that_brings(Capability.skill("JAVA-MID"))
            .that_is_available_at(self.JAN_1)
            .with_employee(self.LEON)
            .that_brings(Capability.skill("JAVA-MID"))
            .that_is_available_at(self.JAN_1)
            .build()
        )

        # when
        result: Result = (
            self.simulation_facade.which_project_with_missing_demands_is_most_profitable_to_allocate_resources_to(
                simulated_projects, simulated_availability
            )
        )

        # then
        self.assertEqual(99.0, result.profit)
        self.assertEqual(1, len(result.chosen_projects))

    def test_can_simulate_having_extra_resources(self) -> None:
        # given
        simulated_projects: list[SimulatedProject] = (
            self.simulated_projects()
            .with_project(self.PROJECT_1)
            .that_requires(Demand.demand_for(Capability.skill("YT DRAMA COMMENTS"), self.JAN_1))
            .that_can_earn(Decimal(9))
            .with_project(self.PROJECT_2)
            .that_requires(Demand.demand_for(Capability.skill("YT DRAMA COMMENTS"), self.JAN_1))
            .that_can_earn(Decimal(99))
            .build()
        )

        # and there are
        simulated_availability: SimulatedCapabilities = (
            self.simulated_capabilities()
            .with_employee(self.STASZEK)
            .that_brings(Capability.skill("YT DRAMA COMMENTS"))
            .that_is_available_at(self.JAN_1)
            .build()
        )

        # and there are
        extra_capability: AvailableResourceCapability = AvailableResourceCapability(
            uuid.uuid4(), Capability.skill("YT DRAMA COMMENTS"), self.JAN_1
        )

        # when
        result_without_extra_resource: Result = (
            self.simulation_facade.which_project_with_missing_demands_is_most_profitable_to_allocate_resources_to(
                simulated_projects, simulated_availability
            )
        )
        result_with_extra_resource: Result = (
            self.simulation_facade.which_project_with_missing_demands_is_most_profitable_to_allocate_resources_to(
                simulated_projects, simulated_availability.add(extra_capability)
            )
        )

        # then
        self.assertEqual(99.0, result_without_extra_resource.profit)
        self.assertEqual(108.0, result_with_extra_resource.profit)

    def simulated_projects(self) -> SimulatedProjectsBuilder:
        return SimulatedProjectsBuilder()

    def simulated_capabilities(self) -> AvailableCapabilitiesBuilder:
        return AvailableCapabilitiesBuilder()
