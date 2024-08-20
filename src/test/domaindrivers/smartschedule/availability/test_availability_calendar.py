from datetime import timedelta
from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from unittest import TestCase

from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.availability.calendar import Calendar
from domaindrivers.smartschedule.availability.calendars import Calendars
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestAvailabilityCalendar(TestCase):
    SQL_SCRIPTS: tuple[str] = ("schema-availability.sql",)
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)
    availability_facade: AvailabilityFacade

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.availability_facade = dependency_resolver.resolve_dependency(AvailabilityFacade)

    def test_loads_calendar_for_entire_month(self) -> None:
        # given
        resource_id: ResourceId = ResourceId.new_one()
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        fifteen_minutes: TimeSlot = TimeSlot(
            one_day.since + timedelta(minutes=15), one_day.since + timedelta(minutes=30)
        )
        owner: Owner = Owner.new_one()
        # and
        self.availability_facade.create_resource_slots(resource_id, one_day)

        # when
        self.availability_facade.block(resource_id, fifteen_minutes, owner)

        # then
        calendar: Calendar = self.availability_facade.load_calendar(resource_id, one_day)
        self.assertEqual(calendar.taken_by(owner), [fifteen_minutes])
        for slot in one_day.leftover_after_removing_common_with(fifteen_minutes):
            self.assertTrue(slot in calendar.available_slots())
        self.assertEqual(
            len(calendar.available_slots()), len(one_day.leftover_after_removing_common_with(fifteen_minutes))
        )

    def test_loads_calendar_for_multiple_resources(self) -> None:
        # given
        resource_id: ResourceId = ResourceId.new_one()
        resource_id_2: ResourceId = ResourceId.new_one()
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        fifteen_minutes: TimeSlot = TimeSlot(
            one_day.since + timedelta(minutes=15), one_day.since + timedelta(minutes=30)
        )
        owner: Owner = Owner.new_one()
        self.availability_facade.create_resource_slots(resource_id, one_day)
        self.availability_facade.create_resource_slots(resource_id_2, one_day)

        # when
        self.availability_facade.block(resource_id, fifteen_minutes, owner)
        self.availability_facade.block(resource_id_2, fifteen_minutes, owner)

        # then
        calendars: Calendars = self.availability_facade.load_calendars({resource_id, resource_id_2}, one_day)
        self.assertEqual(calendars.get(resource_id).taken_by(owner), [fifteen_minutes])
        self.assertEqual(calendars.get(resource_id_2).taken_by(owner), [fifteen_minutes])

        for slot in one_day.leftover_after_removing_common_with(fifteen_minutes):
            self.assertTrue(slot in calendars.get(resource_id).available_slots())
            self.assertTrue(slot in calendars.get(resource_id_2).available_slots())
        self.assertEqual(
            len(calendars.get(resource_id).available_slots()),
            len(one_day.leftover_after_removing_common_with(fifteen_minutes)),
        )
        self.assertEqual(
            len(calendars.get(resource_id_2).available_slots()),
            len(one_day.leftover_after_removing_common_with(fifteen_minutes)),
        )
