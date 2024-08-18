from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from unittest import TestCase
from uuid import UUID

from domaindrivers.smartschedule.allocation.allocated_capability import AllocatedCapability
from domaindrivers.smartschedule.allocation.allocation_facade import AllocationFacade
from domaindrivers.smartschedule.allocation.demand import Demand
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.allocation.projects_allocations_summary import ProjectsAllocationsSummary
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.utils.optional import Optional


class TestCapabilityAllocating(TestCase):
    SQL_SCRIPTS: tuple[str] = ("schema-allocations.sql",)
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)
    allocation_facade: AllocationFacade

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.allocation_facade = dependency_resolver.resolve_dependency(AllocationFacade)

    def test_can_allocate_capability_to_project(self) -> None:
        # given
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        skill_java: Capability = Capability.skill("JAVA")
        demand: Demand = Demand(skill_java, one_day)
        # and
        allocatable_resource_id: ResourceId = ResourceId.new_one()
        # and

        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        # and
        self.allocation_facade.schedule_project_allocation_demands(project_id, Demands.of(demand))

        # when
        result: Optional[UUID] = self.allocation_facade.allocate_to_project(
            project_id, allocatable_resource_id, skill_java, one_day
        )

        # then
        self.assertTrue(result.is_present())
        summary: ProjectsAllocationsSummary = self.allocation_facade.find_all_projects_allocations()
        self.assertTrue(
            AllocatedCapability.of(allocatable_resource_id.get_id(), skill_java, one_day)
            in summary.project_allocations.get(project_id).all
        )
        self.assertTrue(demand in summary.demands.get(project_id).all)

    def test_can_release_capability_from_project(self) -> None:
        # given
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        # and
        allocatable_resource_id: ResourceId = ResourceId.new_one()
        # and
        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        # and
        self.allocation_facade.schedule_project_allocation_demands(project_id, Demands.none())
        # and
        chosen_capability: Capability = Capability.skill("JAVA")
        allocated_id: Optional[UUID] = self.allocation_facade.allocate_to_project(
            project_id, allocatable_resource_id, chosen_capability, one_day
        )

        # when
        result: bool = self.allocation_facade.release_from_project(project_id, allocated_id.get(), one_day)

        # then
        self.assertTrue(result)
        summary: ProjectsAllocationsSummary = self.allocation_facade.find_all_projects_allocations()
        self.assertEqual(summary.project_allocations.get(project_id).all, set())
