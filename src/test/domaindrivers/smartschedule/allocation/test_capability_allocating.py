from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from typing import Final
from unittest import TestCase

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
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.capability_selector import CapabilitySelector
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestCapabilityAllocating(TestCase):
    SQL_SCRIPTS: tuple[str, ...] = ("schema-allocations.sql", "schema-availability.sql")
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)

    ALLOCATABLE_RESOURCE_ID: Final[AllocatableResourceId] = AllocatableResourceId.new_one()
    ALLOCATABLE_RESOURCE_ID_2: Final[AllocatableResourceId] = AllocatableResourceId.new_one()
    ALLOCATABLE_RESOURCE_ID_3: Final[AllocatableResourceId] = AllocatableResourceId.new_one()

    allocation_facade: AllocationFacade
    availability_facade: AvailabilityFacade
    capability_scheduler: CapabilityScheduler

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.allocation_facade = dependency_resolver.resolve_dependency(AllocationFacade)
        self.availability_facade = dependency_resolver.resolve_dependency(AvailabilityFacade)
        self.capability_scheduler = dependency_resolver.resolve_dependency(CapabilityScheduler)

    def test_can_allocate_any_capability_of_required_type(self) -> None:
        # given
        java_and_python: CapabilitySelector = CapabilitySelector.can_perform_one_of(
            Capability.skills("JAVA11", "PYTHON")
        )
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        # and
        allocatable_capability_id_1: AllocatableCapabilityId = self.schedule_capabilities(
            self.ALLOCATABLE_RESOURCE_ID, java_and_python, one_day
        )
        allocatable_capability_id_2: AllocatableCapabilityId = self.schedule_capabilities(
            self.ALLOCATABLE_RESOURCE_ID_2, java_and_python, one_day
        )
        allocatable_capability_id_3: AllocatableCapabilityId = self.schedule_capabilities(
            self.ALLOCATABLE_RESOURCE_ID_3, java_and_python, one_day
        )
        # and
        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        self.allocation_facade.schedule_project_allocation_demands(project_id, Demands.none())

        # when
        result: bool = self.allocation_facade.allocate_capability_to_project_for_period(
            project_id, Capability.skill("JAVA11"), one_day
        )

        # then
        self.assertTrue(result)
        allocated_capabilities: set[AllocatableCapabilityId] = self.load_project_allocations(project_id)
        self.assertTrue(
            any(
                capability in allocated_capabilities
                for capability in (
                    allocatable_capability_id_1,
                    allocatable_capability_id_2,
                    allocatable_capability_id_3,
                )
            )
        )
        self.assertTrue(self.availability_was_blocked(allocated_capabilities, one_day, project_id))

    def test_cant_allocate_any_capability_of_required_type_when_no_capabilities(self) -> None:
        # given
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        # and
        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        # and
        self.allocation_facade.schedule_project_allocation_demands(project_id, Demands.none())

        # when
        result: bool = self.allocation_facade.allocate_capability_to_project_for_period(
            project_id, Capability.skill("DEBUGGING"), one_day
        )

        # then
        self.assertFalse(result)
        summary: ProjectsAllocationsSummary = self.allocation_facade.find_all_projects_allocations()
        self.assertFalse(summary.project_allocations.get(project_id).all)

    def test_cant_allocate_any_capability_of_required_type_when_all_capabilities_taken(self) -> None:
        # given
        capability: CapabilitySelector = CapabilitySelector.can_perform_one_of(Capability.skills("DEBUGGING"))
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)

        allocatable_capability_id_1: AllocatableCapabilityId = self.schedule_capabilities(
            self.ALLOCATABLE_RESOURCE_ID, capability, one_day
        )
        allocatable_capability_id_2: AllocatableCapabilityId = self.schedule_capabilities(
            self.ALLOCATABLE_RESOURCE_ID_2, capability, one_day
        )
        # and
        project_1: ProjectAllocationsId = self.allocation_facade.create_allocation(
            one_day, Demands.of(Demand(Capability.skill("DEBUGGING"), one_day))
        )
        project_2: ProjectAllocationsId = self.allocation_facade.create_allocation(
            one_day, Demands.of(Demand(Capability.skill("DEBUGGING"), one_day))
        )
        # and
        self.allocation_facade.allocate_to_project(project_1, allocatable_capability_id_1, one_day)
        self.allocation_facade.allocate_to_project(project_2, allocatable_capability_id_2, one_day)

        # and
        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        self.allocation_facade.schedule_project_allocation_demands(project_id, Demands.none())

        # when
        result: bool = self.allocation_facade.allocate_capability_to_project_for_period(
            project_id, Capability.skill("DEBUGGING"), one_day
        )

        # then
        self.assertFalse(result)
        summary: ProjectsAllocationsSummary = self.allocation_facade.find_all_projects_allocations()
        self.assertFalse(summary.project_allocations.get(project_id).all)

    def load_project_allocations(self, project_id_1: ProjectAllocationsId) -> set[AllocatableCapabilityId]:
        summary: ProjectsAllocationsSummary = self.allocation_facade.find_all_projects_allocations()
        allocated_capabilities: set[AllocatableCapabilityId] = set(
            map(
                lambda allocated_capability: allocated_capability.allocated_capability_id,
                summary.project_allocations.get(project_id_1).all,
            )
        )
        return allocated_capabilities

    def schedule_capabilities(
        self, allocatable_resource_id: AllocatableResourceId, capabilities: CapabilitySelector, one_day: TimeSlot
    ) -> AllocatableCapabilityId:
        allocatable_capability_ids: list[AllocatableCapabilityId] = (
            self.capability_scheduler.schedule_resource_capabilities_for_period(
                allocatable_resource_id, [capabilities], one_day
            )
        )
        self.assertEqual(len(allocatable_capability_ids), 1)
        return allocatable_capability_ids[0]

    def availability_was_blocked(
        self, capabilities: set[AllocatableCapabilityId], one_day: TimeSlot, project_id: ProjectAllocationsId
    ) -> bool:
        calendars: Calendars = self.availability_facade.load_calendars(
            set(
                map(
                    lambda allocatable_capability_id: allocatable_capability_id.to_availability_resource_id(),
                    capabilities,
                )
            ),
            one_day,
        )
        return all(
            calendar.taken_by(Owner.of(project_id.id())) == [one_day] for calendar in calendars.calendars.values()
        )
