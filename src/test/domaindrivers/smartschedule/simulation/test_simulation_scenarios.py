import uuid
from decimal import Decimal
from unittest import TestCase
from uuid import UUID

from domaindrivers.smartschedule.optimization.optimization_facade import OptimizationFacade
from domaindrivers.smartschedule.optimization.result import Result
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.smartschedule.simulation.additional_priced_capability import AdditionalPricedCapability
from domaindrivers.smartschedule.simulation.available_resource_capability import AvailableResourceCapability
from domaindrivers.smartschedule.simulation.demand import Demand
from domaindrivers.smartschedule.simulation.project_id import ProjectId
from domaindrivers.smartschedule.simulation.simulated_capabilities import SimulatedCapabilities
from domaindrivers.smartschedule.simulation.simulated_project import SimulatedProject
from domaindrivers.smartschedule.simulation.simulation_facade import SimulationFacade

from .available_capabilities_builder import AvailableCapabilitiesBuilder
from .simulated_projects_builder import SimulatedProjectsBuilder


class TestSimulationScenarios(TestCase):
    JAN_1: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
    PROJECT_1: ProjectId = ProjectId.new_one()
    PROJECT_2: ProjectId = ProjectId.new_one()
    PROJECT_3: ProjectId = ProjectId.new_one()
    STASZEK: UUID = uuid.uuid4()
    LEON: UUID = uuid.uuid4()

    simulation_facade: SimulationFacade = SimulationFacade(OptimizationFacade())

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
        result: Result = self.simulation_facade.what_is_the_optimal_setup(simulated_projects, simulated_availability)

        # then
        self.assertEqual(108.0, result.profit)
        self.assertEqual(2, len(result.chosen_items))

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
        result: Result = self.simulation_facade.what_is_the_optimal_setup(simulated_projects, simulated_availability)

        # then
        self.assertEqual(99.0, result.profit)
        self.assertEqual(1, len(result.chosen_items))

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
        extra_capability: AvailableResourceCapability = AvailableResourceCapability.from_capability(
            uuid.uuid4(), Capability.skill("YT DRAMA COMMENTS"), self.JAN_1
        )

        # when
        result_without_extra_resource: Result = self.simulation_facade.what_is_the_optimal_setup(
            simulated_projects, simulated_availability
        )
        result_with_extra_resource: Result = self.simulation_facade.what_is_the_optimal_setup(
            simulated_projects, simulated_availability.add(extra_capability)
        )

        # then
        self.assertEqual(99.0, result_without_extra_resource.profit)
        self.assertEqual(108.0, result_with_extra_resource.profit)

    def test_picks_optimal_project_based_on_reputation(self) -> None:
        # given
        simulated_projects: list[SimulatedProject] = (
            self.simulated_projects()
            .with_project(self.PROJECT_1)
            .that_requires(Demand.demand_for(Capability.skill("JAVA-MID"), self.JAN_1))
            .that_can_generate_reputation_loss(100)
            .with_project(self.PROJECT_2)
            .that_requires(Demand.demand_for(Capability.skill("JAVA-MID"), self.JAN_1))
            .that_can_generate_reputation_loss(40)
            .build()
        )

        # and there are
        simulated_availability: SimulatedCapabilities = (
            self.simulated_capabilities()
            .with_employee(self.STASZEK)
            .that_brings(Capability.skill("JAVA-MID"))
            .that_is_available_at(self.JAN_1)
            .build()
        )

        # when
        result: Result = self.simulation_facade.what_is_the_optimal_setup(simulated_projects, simulated_availability)

        # then
        self.assertEqual(str(self.PROJECT_1), result.chosen_items[0].name)

    def test_check_if_it_pays_off_to_pay_for_capability(self) -> None:
        # given
        simulated_projects: list[SimulatedProject] = (
            self.simulated_projects()
            .with_project(self.PROJECT_1)
            .that_requires(Demand.demand_for(Capability.skill("JAVA-MID"), self.JAN_1))
            .that_can_earn(Decimal(100))
            .with_project(self.PROJECT_2)
            .that_requires(Demand.demand_for(Capability.skill("JAVA-MID"), self.JAN_1))
            .that_can_earn(Decimal(40))
            .build()
        )

        # and there are
        simulated_availability: SimulatedCapabilities = (
            self.simulated_capabilities()
            .with_employee(self.STASZEK)
            .that_brings(Capability.skill("JAVA-MID"))
            .that_is_available_at(self.JAN_1)
            .build()
        )

        # and there are
        slawek: AdditionalPricedCapability = AdditionalPricedCapability(
            Decimal(9999),
            AvailableResourceCapability.from_capability(uuid.uuid4(), Capability.skill("JAVA-MID"), self.JAN_1),
        )
        staszek: AdditionalPricedCapability = AdditionalPricedCapability(
            Decimal(3),
            AvailableResourceCapability.from_capability(uuid.uuid4(), Capability.skill("JAVA-MID"), self.JAN_1),
        )

        # when
        buying_slawek: float = self.simulation_facade.profit_after_buying_new_capability(
            simulated_projects, simulated_availability, slawek
        )
        buying_staszek: float = self.simulation_facade.profit_after_buying_new_capability(
            simulated_projects, simulated_availability, staszek
        )

        # then
        self.assertEqual(Decimal(-9959), buying_slawek)  # we pay 9999 and get the project for 40
        self.assertEqual(Decimal(37), buying_staszek)  # we pay 3 and get the project for 40

    def test_takes_into_account_simulations_capabilities(self) -> None:
        # given
        simulated_projects: list[SimulatedProject] = (
            self.simulated_projects()
            .with_project(self.PROJECT_1)
            .that_requires(Demand.demand_for(Capability.skill("JAVA-MID"), self.JAN_1))
            .that_can_earn(Decimal(9))
            .with_project(self.PROJECT_2)
            .that_requires(Demand.demand_for(Capability.skill("JAVA-MID"), self.JAN_1))
            .that_requires(Demand.demand_for(Capability.skill("PYTHON"), self.JAN_1))
            .that_can_earn(Decimal(99))
            .build()
        )

        # and there are
        simulated_availability: SimulatedCapabilities = (
            self.simulated_capabilities()
            .with_employee(self.STASZEK)
            .that_brings_simultaneously(Capability.skill("JAVA-MID"), Capability.skill("PYTHON"))
            .that_is_available_at(self.JAN_1)
            .build()
        )

        # when
        result: Result = self.simulation_facade.what_is_the_optimal_setup(simulated_projects, simulated_availability)

        # then
        self.assertEqual(99, result.profit)
        self.assertEqual(1, len(result.chosen_items))

    def simulated_projects(self) -> SimulatedProjectsBuilder:
        return SimulatedProjectsBuilder()

    def simulated_capabilities(self) -> AvailableCapabilitiesBuilder:
        return AvailableCapabilitiesBuilder()
