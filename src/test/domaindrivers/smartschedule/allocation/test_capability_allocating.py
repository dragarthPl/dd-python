from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from unittest import TestCase
from uuid import UUID

from domaindrivers.smartschedule.allocation.allocated_capability import AllocatedCapability
from domaindrivers.smartschedule.allocation.allocation_facade import AllocationFacade
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_resource_id import AllocatableResourceId
from domaindrivers.smartschedule.allocation.capabilityscheduling.capability_scheduler import CapabilityScheduler
from domaindrivers.smartschedule.allocation.demand import Demand
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.allocation.projects_allocations_summary import ProjectsAllocationsSummary
from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.availability.calendars import Calendars
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.capability_selector import CapabilitySelector
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.utils.optional import Optional


class TestCapabilityAllocating(TestCase):
    SQL_SCRIPTS: tuple[str, ...] = ("schema-allocations.sql", "schema-availability.sql")
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)

    RESOURCE_ID: AllocatableResourceId = AllocatableResourceId.new_one()
    allocation_facade: AllocationFacade
    availability_facade: AvailabilityFacade
    capability_scheduler: CapabilityScheduler

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.allocation_facade = dependency_resolver.resolve_dependency(AllocationFacade)
        self.availability_facade = dependency_resolver.resolve_dependency(AvailabilityFacade)
        self.capability_scheduler = dependency_resolver.resolve_dependency(CapabilityScheduler)

    def test_can_allocate_capability_to_project(self) -> None:
        # given
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        skill_java: Capability = Capability.skill("JAVA")
        demand: Demand = Demand(skill_java, one_day)
        # and
        allocatable_capability_id: AllocatableCapabilityId = self.create_allocatable_resource(
            one_day, skill_java, self.RESOURCE_ID
        )
        # and

        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        # and
        self.allocation_facade.schedule_project_allocation_demands(project_id, Demands.of(demand))

        # when
        result: Optional[UUID] = self.allocation_facade.allocate_to_project(
            project_id, allocatable_capability_id, skill_java, one_day
        )

        # then
        self.assertTrue(result.is_present())
        summary: ProjectsAllocationsSummary = self.allocation_facade.find_all_projects_allocations()
        self.assertTrue(
            AllocatedCapability(allocatable_capability_id, skill_java, one_day)
            in summary.project_allocations.get(project_id).all
        )
        self.assertTrue(demand in summary.demands.get(project_id).all)
        self.assertTrue(
            self.availability_was_blocked(allocatable_capability_id.to_availability_resource_id(), one_day, project_id)
        )

    def test_cant_allocate_when_resource_not_available(self) -> None:
        # given
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        skill_java: Capability = Capability.skill("JAVA")
        demand: Demand = Demand(skill_java, one_day)
        # and
        allocatable_capability_id: AllocatableCapabilityId = self.create_allocatable_resource(
            one_day, skill_java, self.RESOURCE_ID
        )
        # and
        self.availability_facade.block(
            allocatable_capability_id.to_availability_resource_id(), one_day, Owner.new_one()
        )
        # and
        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        # and
        self.allocation_facade.schedule_project_allocation_demands(project_id, Demands.of(demand))

        # when
        result: Optional[UUID] = self.allocation_facade.allocate_to_project(
            project_id, allocatable_capability_id, skill_java, one_day
        )

        # then
        self.assertFalse(result.is_present())
        summary: ProjectsAllocationsSummary = self.allocation_facade.find_all_projects_allocations()
        self.assertTrue(not summary.project_allocations.get(project_id).all)

    def test_cant_allocate_when_capability_has_not_been_scheduled(self) -> None:
        # given
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        skill_java: Capability = Capability.skill("JAVA")
        demand: Demand = Demand(skill_java, one_day)
        # and
        not_scheduled_capability: AllocatableCapabilityId = AllocatableCapabilityId.new_one()
        # and
        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        # and
        self.allocation_facade.schedule_project_allocation_demands(project_id, Demands.of(demand))

        # when
        result: Optional[UUID] = self.allocation_facade.allocate_to_project(
            project_id, not_scheduled_capability, skill_java, one_day
        )

        # then
        self.assertFalse(result.is_present())
        summary: ProjectsAllocationsSummary = self.allocation_facade.find_all_projects_allocations()
        self.assertTrue(not summary.project_allocations.get(project_id).all)

    def test_can_release_capability_from_project(self) -> None:
        # given
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        # and
        allocatable_capability_id: AllocatableCapabilityId = self.create_allocatable_resource(
            one_day, Capability.skill("JAVA"), self.RESOURCE_ID
        )
        # and
        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        # and
        self.allocation_facade.schedule_project_allocation_demands(project_id, Demands.none())
        # and
        chosen_capability: Capability = Capability.skill("JAVA")
        self.allocation_facade.allocate_to_project(project_id, allocatable_capability_id, chosen_capability, one_day)

        # when
        result: bool = self.allocation_facade.release_from_project(project_id, allocatable_capability_id, one_day)

        # then
        self.assertTrue(result)
        summary: ProjectsAllocationsSummary = self.allocation_facade.find_all_projects_allocations()
        self.assertEqual(summary.project_allocations.get(project_id).all, set())
        self.assertTrue(self.availability_is_released(one_day, allocatable_capability_id, project_id))

    def create_allocatable_resource(
        self, period: TimeSlot, capability: Capability, resource_id: AllocatableResourceId
    ) -> AllocatableCapabilityId:
        capabilities: list[CapabilitySelector] = [CapabilitySelector.can_just_perform(capability)]
        allocatable_capability_ids: list[AllocatableCapabilityId] = (
            self.capability_scheduler.schedule_resource_capabilities_for_period(resource_id, capabilities, period)
        )
        self.assertEqual(len(allocatable_capability_ids), 1)
        return allocatable_capability_ids[0]

    def availability_was_blocked(
        self, resource: ResourceId, period: TimeSlot, project_id: ProjectAllocationsId
    ) -> bool:
        calendars: Calendars = self.availability_facade.load_calendars({resource}, period)
        return all(
            [calendar.taken_by(Owner.of(project_id.id())) == [period] for calendar in calendars.calendars.values()]
        )

    def availability_is_released(
        self, one_day: TimeSlot, allocatable_capability_id: AllocatableCapabilityId, project_id: ProjectAllocationsId
    ) -> bool:
        return not self.availability_was_blocked(
            allocatable_capability_id.to_availability_resource_id(), one_day, project_id
        )
