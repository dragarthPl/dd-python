from datetime import datetime
from unittest import TestCase

import pytz
from domaindrivers.smartschedule.shared.time_slot import TimeSlot


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
