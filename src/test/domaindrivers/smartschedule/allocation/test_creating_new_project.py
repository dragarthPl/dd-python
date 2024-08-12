from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from unittest import TestCase

from domaindrivers.smartschedule.allocation.allocation_facade import AllocationFacade
from domaindrivers.smartschedule.allocation.demand import Demand
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.allocation.projects_allocations_summary import ProjectsAllocationsSummary
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestCreatingNewProject(TestCase):
    SQL_SCRIPTS: tuple[str] = ("schema-allocations.sql",)
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)
    allocation_facade: AllocationFacade

    JAN: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
    FEB: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 2, 1)

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.allocation_facade = dependency_resolver.resolve_dependency(AllocationFacade)

    def test_can_create_new_project(self) -> None:
        # given
        demand: Demand = Demand(Capability.skill("JAVA"), self.JAN)

        # when
        demands: Demands = Demands.of(demand)
        new_project: ProjectAllocationsId = self.allocation_facade.create_allocation(self.JAN, demands)

        # then
        summary: ProjectsAllocationsSummary = self.allocation_facade.find_all_projects_allocations_by({new_project})
        self.assertEqual(summary.demands.get(new_project), demands)
        self.assertEqual(summary.time_slots.get(new_project), self.JAN)

    def test_can_redefine_project_deadline(self) -> None:
        # given
        demand: Demand = Demand(Capability.skill("JAVA"), self.JAN)
        # and
        demands: Demands = Demands.of(demand)
        new_project: ProjectAllocationsId = self.allocation_facade.create_allocation(self.JAN, demands)

        # when
        self.allocation_facade.edit_project_dates(new_project, self.FEB)

        # then
        summary: ProjectsAllocationsSummary = self.allocation_facade.find_all_projects_allocations_by({new_project})
        self.assertEqual(summary.time_slots.get(new_project), self.FEB)
