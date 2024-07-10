from datetime import datetime
from unittest import TestCase

import pytz
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestTimeSlot(TestCase):
    def test_creating_monthly_time_slot_at_utc(self) -> None:
        # when
        january2023: TimeSlot = TimeSlot.create_monthly_time_slot_at_utc(2023, 1)

        # then
        self.assertEqual(january2023.since, datetime(2023, 1, 1).astimezone(pytz.utc))
        self.assertEqual(january2023.to, datetime(2023, 2, 1).astimezone(pytz.utc))

    def test_creating_daily_time_slot_at_utc(self) -> None:
        # when
        specific_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2023, 1, 15)

        # then
        self.assertEqual(specific_day.since, datetime(2023, 1, 15).astimezone(pytz.utc))
        self.assertEqual(specific_day.to, datetime(2023, 1, 16).astimezone(pytz.utc))

    def test_one_slot_within_another(self) -> None:
        # given
        slot1: TimeSlot = TimeSlot(
            datetime.strptime("2023-01-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2023-01-02T23:59:59Z", "%Y-%m-%dT%H:%M:%SZ"),
        )
        slot2: TimeSlot = TimeSlot(
            datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2023-01-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )
        # expect
        self.assertTrue(slot1.within(slot2))
        self.assertFalse(slot2.within(slot1))

    def test_one_slot_is_not_within_another_if_they_just_overlap(self) -> None:
        # given
        slot1: TimeSlot = TimeSlot(
            datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2023-01-02T23:59:59Z", "%Y-%m-%dT%H:%M:%SZ"),
        )
        slot2: TimeSlot = TimeSlot(
            datetime.strptime("2023-01-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2023-01-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )

        # expect
        self.assertFalse(slot1.within(slot2))
        self.assertFalse(slot2.within(slot1))

        # given
        slot3: TimeSlot = TimeSlot(
            datetime.strptime("2023-01-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2023-01-03T23:59:59Z", "%Y-%m-%dT%H:%M:%SZ"),
        )
        slot4: TimeSlot = TimeSlot(
            datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2023-01-02T23:59:59Z", "%Y-%m-%dT%H:%M:%SZ"),
        )

        # expect
        self.assertFalse(slot3.within(slot4))
        self.assertFalse(slot4.within(slot3))

    def test_slot_is_not_within_another_when_they_are_completely_outside(self) -> None:
        # given
        slot1: TimeSlot = TimeSlot(
            datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2023-01-01T23:59:59Z", "%Y-%m-%dT%H:%M:%SZ"),
        )
        slot2: TimeSlot = TimeSlot(
            datetime.strptime("2023-01-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2023-01-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )

        # expect
        self.assertFalse(slot1.within(slot2))

    def test_slot_is_within_itself(self) -> None:
        # given
        slot1: TimeSlot = TimeSlot(
            datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2023-01-01T23:59:59Z", "%Y-%m-%dT%H:%M:%SZ"),
        )

        # expect
        self.assertTrue(slot1.within(slot1))

    def test_slots_overlapping(self) -> None:
        # given
        slot1: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )
        slot2: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-05T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-15T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )
        slot3: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-20T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )
        slot4: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-05T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )
        slot5: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )

        # expect
        self.assertTrue(slot1.overlaps_with(slot2))
        self.assertTrue(slot1.overlaps_with(slot1))
        self.assertTrue(slot1.overlaps_with(slot3))
        self.assertTrue(slot1.overlaps_with(slot4))
        self.assertTrue(slot1.overlaps_with(slot5))

    def test_slots_not_overlapping(self) -> None:
        # given
        slot1: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )
        slot2: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-10T01:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-20T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )
        slot3: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-11T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-20T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )

        # expect
        self.assertFalse(slot1.overlaps_with(slot2))
        self.assertFalse(slot1.overlaps_with(slot3))

    def test_removing_common_parts_should_have_no_effect_when_there_is_no_overlap(self) -> None:
        # given
        slot1: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )
        slot2: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-15T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-20T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )

        # expect
        leftover_after_removing_common_with = slot1.leftover_after_removing_common_with(slot2)
        self.assertTrue(
            all((slot1 in leftover_after_removing_common_with, slot2 in leftover_after_removing_common_with))
        )

    def test_removing_common_parts_when_there_is_full_overlap(self) -> None:
        # given
        slot1: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )

        # expect
        self.assertTrue(slot1.leftover_after_removing_common_with(slot1) == [])

    def test_removing_common_parts_when_there_is_overlap(self) -> None:
        # given
        slot1: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-15T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )
        slot2: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-20T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )

        # when
        difference: list[TimeSlot] = slot1.leftover_after_removing_common_with(slot2)

        # then
        self.assertEqual(2, len(difference))
        self.assertEqual(datetime.strptime("2022-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), difference[0].since)
        self.assertEqual(datetime.strptime("2022-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), difference[0].to)
        self.assertEqual(datetime.strptime("2022-01-15T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), difference[1].since)
        self.assertEqual(datetime.strptime("2022-01-20T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), difference[1].to)

        # given
        slot3: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-05T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-20T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )
        slot4: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )

        # when
        difference2: list[TimeSlot] = slot3.leftover_after_removing_common_with(slot4)

        # then
        self.assertEqual(2, len(difference2))
        self.assertEqual(datetime.strptime("2022-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), difference2[0].since)
        self.assertEqual(datetime.strptime("2022-01-05T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), difference2[0].to)
        self.assertEqual(datetime.strptime("2022-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), difference2[1].since)
        self.assertEqual(datetime.strptime("2022-01-20T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), difference2[1].to)

    def test_removing_common_part_when_one_slot_in_fully_within_another(self) -> None:
        # given
        slot1: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-20T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )
        slot2: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-15T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )

        # when
        difference: list[TimeSlot] = slot1.leftover_after_removing_common_with(slot2)

        # then
        self.assertEqual(2, len(difference))
        self.assertEqual(datetime.strptime("2022-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), difference[0].since)
        self.assertEqual(datetime.strptime("2022-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), difference[0].to)
        self.assertEqual(datetime.strptime("2022-01-15T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), difference[1].since)
        self.assertEqual(datetime.strptime("2022-01-20T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), difference[1].to)
