from datetime import timedelta
from unittest import TestCase

from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestAvailabilityFacade(TestCase):
    availability_facade: AvailabilityFacade = AvailabilityFacade()

    def test_can_create_availability_slots(self) -> None:
        # given
        resource_id: ResourceAvailabilityId = ResourceAvailabilityId.new_one()
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)

        # when
        self.availability_facade.create_resource_slots(resource_id, one_day)

        # then
        # todo check that availability(ies) was/were created

    def test_can_block_availabilities(self) -> None:
        # given
        resource_id: ResourceAvailabilityId = ResourceAvailabilityId.new_one()
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        owner: Owner = Owner.new_one()
        self.availability_facade.create_resource_slots(resource_id, one_day)

        # when
        result: bool = self.availability_facade.block(resource_id, one_day, owner)

        # then
        self.assertTrue(result)
        # todo check that can't be taken

    def test_can_disable_availabilities(self) -> None:
        # given
        resource_id: ResourceAvailabilityId = ResourceAvailabilityId.new_one()
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        owner: Owner = Owner.new_one()
        self.availability_facade.create_resource_slots(resource_id, one_day)

        # when
        result: bool = self.availability_facade.disable(resource_id, one_day, owner)

        # then
        self.assertTrue(result)
        # todo check that are disabled

    def test_cant_block_even_when_just_small_segment_of_requested_slot_is_blocked(self) -> None:
        # given
        resource_id: ResourceAvailabilityId = ResourceAvailabilityId.new_one()
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
        # todo check that nothing was changed

    def test_can_release_availability(self) -> None:
        # given
        resource_id: ResourceAvailabilityId = ResourceAvailabilityId.new_one()
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
        # todo check can be taken again

    def test_cant_release_even_when_just_part_of_slot_is_owned_by_the_requester(self) -> None:
        # given
        resource_id: ResourceAvailabilityId = ResourceAvailabilityId.new_one()
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
        # todo check still owned by jan1
