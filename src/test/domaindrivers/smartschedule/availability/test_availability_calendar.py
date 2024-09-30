from datetime import timedelta
from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from unittest import TestCase

from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.availability.calendar import Calendar
from domaindrivers.smartschedule.availability.calendars import Calendars
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.availability.segment.segments import Segments
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
        duration_of_seven_slots: timedelta = timedelta(minutes=7 * Segments.DEFAULT_SEGMENT_DURATION_IN_MINUTES)
        seven_slots: TimeSlot = TimeSlot.create_time_slot_at_utc_of_duration(2021, 1, 1, duration_of_seven_slots)
        minimum_slot: TimeSlot = TimeSlot(
            seven_slots.since, seven_slots.since + timedelta(minutes=Segments.DEFAULT_SEGMENT_DURATION_IN_MINUTES)
        )

        owner: Owner = Owner.new_one()
        # and
        self.availability_facade.create_resource_slots(resource_id, seven_slots)

        # when
        self.availability_facade.block(resource_id, minimum_slot, owner)

        # then
        calendar: Calendar = self.availability_facade.load_calendar(resource_id, seven_slots)
        self.assertEqual(calendar.taken_by(owner), [minimum_slot])
        for slot in seven_slots.leftover_after_removing_common_with(minimum_slot):
            self.assertTrue(slot in calendar.available_slots())
        self.assertEqual(
            len(calendar.available_slots()), len(seven_slots.leftover_after_removing_common_with(minimum_slot))
        )

    def test_loads_calendar_for_multiple_resources(self) -> None:
        # given
        resource_id: ResourceId = ResourceId.new_one()
        resource_id_2: ResourceId = ResourceId.new_one()
        duration_of_seven_slots: timedelta = timedelta(minutes=7 * Segments.DEFAULT_SEGMENT_DURATION_IN_MINUTES)
        seven_slots: TimeSlot = TimeSlot.create_time_slot_at_utc_of_duration(2021, 1, 1, duration_of_seven_slots)
        minimum_slot: TimeSlot = TimeSlot(
            seven_slots.since, seven_slots.since + timedelta(minutes=Segments.DEFAULT_SEGMENT_DURATION_IN_MINUTES)
        )

        owner: Owner = Owner.new_one()
        self.availability_facade.create_resource_slots(resource_id, seven_slots)
        self.availability_facade.create_resource_slots(resource_id_2, seven_slots)

        # when
        self.availability_facade.block(resource_id, minimum_slot, owner)
        self.availability_facade.block(resource_id_2, minimum_slot, owner)

        # then
        calendars: Calendars = self.availability_facade.load_calendars({resource_id, resource_id_2}, seven_slots)
        self.assertEqual(calendars.get(resource_id).taken_by(owner), [minimum_slot])
        self.assertEqual(calendars.get(resource_id_2).taken_by(owner), [minimum_slot])

        for slot in seven_slots.leftover_after_removing_common_with(minimum_slot):
            self.assertTrue(slot in calendars.get(resource_id).available_slots())
            self.assertTrue(slot in calendars.get(resource_id_2).available_slots())
        self.assertEqual(
            len(calendars.get(resource_id).available_slots()),
            len(seven_slots.leftover_after_removing_common_with(minimum_slot)),
        )
        self.assertEqual(
            len(calendars.get(resource_id_2).available_slots()),
            len(seven_slots.leftover_after_removing_common_with(minimum_slot)),
        )
