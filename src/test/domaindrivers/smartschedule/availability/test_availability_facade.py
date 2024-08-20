from datetime import timedelta
from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from unittest import TestCase

from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.availability.calendar import Calendar
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_grouped_availability import ResourceGroupedAvailability
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestAvailabilityFacade(TestCase):
    SQL_SCRIPTS: tuple[str] = ("schema-availability.sql",)
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)
    availability_facade: AvailabilityFacade

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.availability_facade = dependency_resolver.resolve_dependency(AvailabilityFacade)

    def test_can_create_availability_slots(self) -> None:
        # given
        resource_id: ResourceId = ResourceId.new_one()
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)

        # when
        self.availability_facade.create_resource_slots(resource_id, one_day)

        # then
        entire_month: TimeSlot = TimeSlot.create_monthly_time_slot_at_utc(2021, 1)
        monthly_calendar: Calendar = self.availability_facade.load_calendar(resource_id, entire_month)
        self.assertEqual(monthly_calendar, Calendar.with_available_slots(resource_id, one_day))

    def test_can_create_new_availability_slots_with_parent_id(self) -> None:
        # given
        resource_id: ResourceId = ResourceId.new_one()
        resource_id_2: ResourceId = ResourceId.new_one()
        parent_id: ResourceId = ResourceId.new_one()
        different_parent_id: ResourceId = ResourceId.new_one()
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)

        # when
        self.availability_facade.create_resource_slots_with_parent_id(resource_id, parent_id, one_day)
        self.availability_facade.create_resource_slots_with_parent_id(resource_id_2, different_parent_id, one_day)

        # then
        self.assertEqual(96, self.availability_facade.find_by_parent_id(parent_id, one_day).size())
        self.assertEqual(96, self.availability_facade.find_by_parent_id(different_parent_id, one_day).size())

    def test_can_block_availabilities(self) -> None:
        # given
        resource_id: ResourceId = ResourceId.new_one()
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        owner: Owner = Owner.new_one()
        self.availability_facade.create_resource_slots(resource_id, one_day)

        # when
        result: bool = self.availability_facade.block(resource_id, one_day, owner)

        # then
        self.assertTrue(result)
        entire_month: TimeSlot = TimeSlot.create_monthly_time_slot_at_utc(2021, 1)
        monthly_calendar: Calendar = self.availability_facade.load_calendar(resource_id, entire_month)
        self.assertTrue(len(monthly_calendar.available_slots()) == 0 or monthly_calendar.available_slots() is None)
        self.assertEqual(monthly_calendar.taken_by(owner), [one_day])

    def test_can_disable_availabilities(self) -> None:
        # given
        resource_id: ResourceId = ResourceId.new_one()
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        owner: Owner = Owner.new_one()
        self.availability_facade.create_resource_slots(resource_id, one_day)

        # when
        result: bool = self.availability_facade.disable(resource_id, one_day, owner)

        # then
        self.assertTrue(result)
        resource_availabilities: ResourceGroupedAvailability = self.availability_facade.find(resource_id, one_day)
        self.assertEqual(96, resource_availabilities.size())
        self.assertTrue(resource_availabilities.is_disabled_entirely_by(owner))

    def test_cant_block_even_when_just_small_segment_of_requested_slot_is_blocked(self) -> None:
        # given
        resource_id: ResourceId = ResourceId.new_one()
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        owner: Owner = Owner.new_one()
        self.availability_facade.create_resource_slots(resource_id, one_day)
        # and
        self.availability_facade.block(resource_id, one_day, owner)
        fifteen_minutes: TimeSlot = TimeSlot(one_day.since, one_day.since + timedelta(minutes=15))

        # when
        result: bool = self.availability_facade.block(resource_id, fifteen_minutes, Owner.new_one())

        # then
        self.assertFalse(result)
        resource_availability: ResourceGroupedAvailability = self.availability_facade.find(resource_id, one_day)
        self.assertTrue(resource_availability.blocked_entirely_by(owner))

    def test_can_release_availability(self) -> None:
        # given
        resource_id: ResourceId = ResourceId.new_one()
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        fifteen_minutes: TimeSlot = TimeSlot(one_day.since, one_day.since + timedelta(minutes=15))
        owner: Owner = Owner.new_one()
        self.availability_facade.create_resource_slots(resource_id, fifteen_minutes)
        # and
        self.availability_facade.block(resource_id, fifteen_minutes, owner)

        # when
        result: bool = self.availability_facade.release(resource_id, one_day, owner)

        # then
        self.assertTrue(result)
        resource_availability: ResourceGroupedAvailability = self.availability_facade.find(resource_id, one_day)
        self.assertTrue(resource_availability.is_entirely_available())

    def test_cant_release_even_when_just_part_of_slot_is_owned_by_the_requester(self) -> None:
        # given
        resource_id: ResourceId = ResourceId.new_one()
        jan_1: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        jan_2: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 2)
        jan_1_2: TimeSlot = TimeSlot(jan_1.since, jan_2.to)
        jan_1_owner: Owner = Owner.new_one()
        self.availability_facade.create_resource_slots(resource_id, jan_1_2)
        # and
        self.availability_facade.block(resource_id, jan_1, jan_1_owner)
        # and
        jan_2_owner: Owner = Owner.new_one()
        self.availability_facade.block(resource_id, jan_2, jan_2_owner)

        # when
        result: bool = self.availability_facade.release(resource_id, jan_1_2, jan_1_owner)

        # then
        self.assertFalse(result)
        resource_availability: ResourceGroupedAvailability = self.availability_facade.find(resource_id, jan_1)
        self.assertTrue(resource_availability.blocked_entirely_by(jan_1_owner))

    def test_one_segment_can_be_taken_by_someone_else_after_realising(self) -> None:
        # given
        resource_id: ResourceId = ResourceId.new_one()
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        fifteen_minutes: TimeSlot = TimeSlot(one_day.since, one_day.since + timedelta(minutes=15))
        owner: Owner = Owner.new_one()
        self.availability_facade.create_resource_slots(resource_id, one_day)
        # and
        self.availability_facade.block(resource_id, one_day, owner)
        # and
        self.availability_facade.release(resource_id, fifteen_minutes, owner)

        # when
        new_requester: Owner = Owner.new_one()
        result: bool = self.availability_facade.block(resource_id, fifteen_minutes, new_requester)

        # then
        self.assertTrue(result)
        daily_calendar: Calendar = self.availability_facade.load_calendar(resource_id, one_day)
        self.assertTrue(not daily_calendar.available_slots())
        taken_by_owner = daily_calendar.taken_by(owner)
        leftover = one_day.leftover_after_removing_common_with(fifteen_minutes)
        self.assertEqual(taken_by_owner, leftover)
        self.assertEqual(daily_calendar.taken_by(new_requester), [fifteen_minutes])
