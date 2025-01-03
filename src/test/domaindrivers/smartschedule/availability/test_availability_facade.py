from datetime import timedelta
from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from typing import Callable, cast, Type
from unittest import TestCase

import mockito
from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.availability.calendar import Calendar
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_grouped_availability import ResourceGroupedAvailability
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.availability.segment.segments import Segments
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher
from domaindrivers.smartschedule.shared.published_event import PublishedEvent
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from mockito import arg_that, mock


class TestAvailabilityFacade(TestCase):
    SQL_SCRIPTS: tuple[str] = ("schema-availability.sql",)
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)
    availability_facade: AvailabilityFacade
    events_publisher: EventsPublisher

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.availability_facade = dependency_resolver.resolve_dependency(
            cast(Type[AvailabilityFacade], AvailabilityFacade)
        )
        self.events_publisher = dependency_resolver.resolve_dependency(cast(Type[EventsPublisher], EventsPublisher))

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
        self.assertTrue(
            self.availability_facade.find_by_parent_id(parent_id, one_day).is_entirely_with_parent_id(parent_id)
        )
        self.assertTrue(
            self.availability_facade.find_by_parent_id(different_parent_id, one_day).is_entirely_with_parent_id(
                different_parent_id
            )
        )

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

    def test_cant_block_when_no_slots_created(self) -> None:
        # given
        resource_id: ResourceId = ResourceId.new_one()
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        owner: Owner = Owner.new_one()

        # when
        result: bool = self.availability_facade.block(resource_id, one_day, owner)

        # then
        self.assertFalse(result)

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
        self.assertTrue(resource_availabilities.is_disabled_entirely_by(owner))

    def test_cant_disable_when_no_slots_created(self) -> None:
        # given
        resource_id: ResourceId = ResourceId.new_one()
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        owner: Owner = Owner.new_one()

        # when
        result: bool = self.availability_facade.disable(resource_id, one_day, owner)

        # then
        self.assertFalse(result)

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

    def test_cant_release_when_no_slots_created(self) -> None:
        # given
        resource_id: ResourceId = ResourceId.new_one()
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        owner: Owner = Owner.new_one()

        # when
        result: bool = self.availability_facade.release(resource_id, one_day, owner)

        # then
        self.assertFalse(result)

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
        duration_of_seven_slots: timedelta = timedelta(minutes=7 * Segments.DEFAULT_SEGMENT_DURATION_IN_MINUTES)
        seven_slots: TimeSlot = TimeSlot.create_time_slot_at_utc_of_duration(2021, 1, 1, duration_of_seven_slots)
        minimum_slot: TimeSlot = TimeSlot(
            seven_slots.since, seven_slots.since + timedelta(minutes=Segments.DEFAULT_SEGMENT_DURATION_IN_MINUTES)
        )

        owner: Owner = Owner.new_one()
        self.availability_facade.create_resource_slots(resource_id, seven_slots)
        # and
        self.availability_facade.block(resource_id, seven_slots, owner)
        # and
        self.availability_facade.release(resource_id, minimum_slot, owner)

        # when
        new_requester: Owner = Owner.new_one()
        result: bool = self.availability_facade.block(resource_id, minimum_slot, new_requester)

        # then
        self.assertTrue(result)
        daily_calendar: Calendar = self.availability_facade.load_calendar(resource_id, seven_slots)
        self.assertTrue(not daily_calendar.available_slots())
        taken_by_owner = daily_calendar.taken_by(owner)
        leftover = seven_slots.leftover_after_removing_common_with(minimum_slot)
        self.assertEqual(taken_by_owner, leftover)
        self.assertEqual(daily_calendar.taken_by(new_requester), [minimum_slot])

    def test_resource_taken_over_event_is_emitted_after_taking_over_the_resource(self) -> None:
        # given
        resource_id: ResourceId = ResourceId.new_one()
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        initial_owner: Owner = Owner.new_one()
        new_owner: Owner = Owner.new_one()
        self.availability_facade._AvailabilityFacade__events_publisher = mock()  # type: ignore[attr-defined]
        self.availability_facade.create_resource_slots(resource_id, one_day)
        self.availability_facade.block(resource_id, one_day, initial_owner)

        # when
        result: bool = self.availability_facade.disable(resource_id, one_day, new_owner)

        # then
        self.assertTrue(result)
        mockito.verify(self.availability_facade._AvailabilityFacade__events_publisher).publish(  # type: ignore[attr-defined]
            arg_that(self.taken_over(resource_id, initial_owner, one_day))
        )

    def taken_over(
        self, resource_id: ResourceId, initial_owner: Owner, one_day: TimeSlot
    ) -> Callable[[PublishedEvent], bool]:
        return lambda event: (
            getattr(event, "resource_id") == resource_id
            and getattr(event, "slot") == one_day
            and getattr(event, "previous_owners") == {initial_owner}
            and event.occurred_at() is not None
            and getattr(event, "event_id") is not None
        )
