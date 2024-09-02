from datetime import timedelta
from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from unittest import TestCase

from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capabilities_summary import (
    AllocatableCapabilitiesSummary,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_summary import (
    AllocatableCapabilitySummary,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_resource_id import AllocatableResourceId
from domaindrivers.smartschedule.allocation.capabilityscheduling.capability_finder import CapabilityFinder
from domaindrivers.smartschedule.allocation.capabilityscheduling.capability_scheduler import CapabilityScheduler
from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.availability.calendar import Calendar
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class CapabilitySchedulingTest(TestCase):
    SQL_SCRIPTS: tuple[str, ...] = (
        "schema-capability-scheduling.sql",
        "schema-availability.sql",
        "schema-allocations.sql",
    )
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)

    capability_scheduler: CapabilityScheduler
    capability_finder: CapabilityFinder
    availability_facade: AvailabilityFacade

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.capability_scheduler = dependency_resolver.resolve_dependency(CapabilityScheduler)
        self.capability_finder = dependency_resolver.resolve_dependency(CapabilityFinder)
        self.availability_facade = dependency_resolver.resolve_dependency(AvailabilityFacade)

    def test_can_schedule_allocatable_capabilities(self) -> None:
        # given
        java_skill: Capability = Capability.skill("JAVA")
        rust_skill: Capability = Capability.skill("RUST")
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)

        # when
        allocatable: list[AllocatableCapabilityId] = (
            self.capability_scheduler.schedule_resource_capabilities_for_period(
                AllocatableResourceId.new_one(), [java_skill, rust_skill], one_day
            )
        )

        # then
        loaded: AllocatableCapabilitiesSummary = self.capability_finder.find_by_id(allocatable)
        self.assertEqual(len(allocatable), len(loaded.all))

        self.assertTrue(
            all(
                self.availability_slots_are_created(allocatable_capability, one_day)
                for allocatable_capability in loaded.all
            )
        )

    def availability_slots_are_created(
        self, allocatable_capability: AllocatableCapabilitySummary, one_day: TimeSlot
    ) -> bool:
        calendar: Calendar = self.availability_facade.load_calendar(
            allocatable_capability.allocatable_capability_id.to_availability_resource_id(), one_day
        )
        return calendar.available_slots() == [one_day]

    def test_capability_is_found_when_capability_present_in_time_slot(self) -> None:
        # given
        unique_skill: Capability = Capability.permission("FITNESS-CLASS")
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        another_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 2)
        # and
        self.capability_scheduler.schedule_resource_capabilities_for_period(
            AllocatableResourceId.new_one(), [unique_skill], one_day
        )

        # when
        found: AllocatableCapabilitiesSummary = self.capability_finder.find_available_capabilities(
            unique_skill, one_day
        )
        not_found: AllocatableCapabilitiesSummary = self.capability_finder.find_available_capabilities(
            unique_skill, another_day
        )

        # then
        self.assertEqual(len(found.all), 1)
        self.assertFalse(bool(not_found.all))
        self.assertEqual(found.all[0].capability, unique_skill)
        self.assertEqual(found.all[0].time_slot, one_day)

    def test_capability_not_found_when_capability_not_present(self) -> None:
        # given
        admin: Capability = Capability.permission("ADMIN")
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        # and
        self.capability_scheduler.schedule_resource_capabilities_for_period(
            AllocatableResourceId.new_one(), [admin], one_day
        )

        # when
        rust: Capability = Capability.skill("RUST JUST FOR NINJAS")
        found: AllocatableCapabilitiesSummary = self.capability_finder.find_capabilities(rust, one_day)

        # then
        self.assertFalse(bool(found.all))

    def test_can_schedule_multiple_capabilities_of_same_type(self) -> None:
        # given
        loading: Capability = Capability.skill("LOADING_TRUCK")
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        # and
        truck1: AllocatableResourceId = AllocatableResourceId.new_one()
        truck2: AllocatableResourceId = AllocatableResourceId.new_one()
        truck3: AllocatableResourceId = AllocatableResourceId.new_one()
        self.capability_scheduler.schedule_multiple_resources_for_period({truck1, truck2, truck3}, loading, one_day)

        # when
        found: AllocatableCapabilitiesSummary = self.capability_finder.find_capabilities(loading, one_day)

        # then
        self.assertEqual(len(found.all), 3)

    def test_can_find_capability_ignoring_availability(self) -> None:
        # given
        admin: Capability = Capability.permission("REALLY_UNIQUE_ADMIN")
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(1111, 1, 1)
        different_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 2, 1)
        hour_within_day: TimeSlot = TimeSlot(one_day.since, one_day.since + timedelta(seconds=3600))
        partially_overlapping_day: TimeSlot = TimeSlot(
            one_day.since + timedelta(seconds=3600), one_day.to + timedelta(seconds=3600)
        )
        # and
        self.capability_scheduler.schedule_resource_capabilities_for_period(
            AllocatableResourceId.new_one(), [admin], one_day
        )

        # when
        on_the_exact_day: AllocatableCapabilitiesSummary = self.capability_finder.find_capabilities(admin, one_day)
        on_different_day: AllocatableCapabilitiesSummary = self.capability_finder.find_capabilities(
            admin, different_day
        )
        in_slot_within: AllocatableCapabilitiesSummary = self.capability_finder.find_capabilities(
            admin, hour_within_day
        )
        in_overlapping_slot: AllocatableCapabilitiesSummary = self.capability_finder.find_capabilities(
            admin, partially_overlapping_day
        )

        # then
        self.assertEqual(len(on_the_exact_day.all), 1)
        self.assertEqual(len(in_slot_within.all), 1)
        self.assertFalse(bool(on_different_day.all))
        self.assertFalse(bool(in_overlapping_slot.all))
