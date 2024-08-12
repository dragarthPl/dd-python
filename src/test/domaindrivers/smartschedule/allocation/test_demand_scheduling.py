from datetime import datetime
from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.fixtures import contains_only_once_elements_of
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from typing import Final
from unittest import TestCase

from domaindrivers.smartschedule.allocation.allocation_facade import AllocationFacade
from domaindrivers.smartschedule.allocation.demand import Demand
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.allocation.projects_allocations_summary import ProjectsAllocationsSummary
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestDemandScheduling(TestCase):
    SQL_SCRIPTS: tuple[str] = ("schema-allocations.sql",)
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)
    allocation_facade: AllocationFacade

    JAVA: Final[Demand] = Demand(Capability.skill("JAVA"), TimeSlot.create_daily_time_slot_at_utc(2022, 2, 2))
    PROJECT_DATES: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2021-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2021-01-06T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.allocation_facade = dependency_resolver.resolve_dependency(AllocationFacade)

    def test_can_schedule_project_demands(self) -> None:
        # given
        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()

        # when
        self.allocation_facade.schedule_project_allocation_demands(project_id, Demands.of(self.JAVA))

        # then
        summary: ProjectsAllocationsSummary = self.allocation_facade.find_all_projects_allocations()
        self.assertTrue(project_id in summary.project_allocations)
        self.assertEqual(len(summary.project_allocations.get(project_id).all), 0)
        for demand in summary.demands.get(project_id).all:
            self.assertEqual(demand, self.JAVA)
        self.assertTrue(contains_only_once_elements_of(summary.demands.get(project_id).all, Demands.of(self.JAVA).all))
