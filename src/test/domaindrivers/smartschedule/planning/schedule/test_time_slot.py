from datetime import datetime, timedelta
from unittest import TestCase

from domaindrivers.smartschedule.planning.schedule.time_slot import TimeSlot


class TestTimeSlot(TestCase):
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

    def twoSlotsHaveCommonPartWhenSlotsOverlap(self) -> None:
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
        common: TimeSlot = slot1.common_part_with(slot2)

        # then
        self.assertFalse(common.is_empty())
        self.assertEqual(datetime.strptime("2022-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), common.since)
        self.assertEqual(datetime.strptime("2022-01-15T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), common.to)

    def test_two_slots_have_common_part_when_full_overlap(self) -> None:
        # given
        slot1: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-20T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )
        slot2: TimeSlot = TimeSlot(
            datetime.strptime("2022-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime("2022-01-20T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        )

        # when
        common: TimeSlot = slot1.common_part_with(slot2)

        # then
        self.assertFalse(common.is_empty())
        self.assertEqual(slot1, common)

    def test_stretch_time_slot(self) -> None:
        # Arrange
        initial_from: datetime = datetime.strptime("2022-01-01T10:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        initial_to: datetime = datetime.strptime("2022-01-01T12:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        time_slot: TimeSlot = TimeSlot(initial_from, initial_to)

        # Act
        stretched_slot: TimeSlot = time_slot.stretch(timedelta(hours=1))

        # Assert
        self.assertEqual(datetime.strptime("2022-01-01T09:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), stretched_slot.since)
        self.assertEqual(datetime.strptime("2022-01-01T13:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), stretched_slot.to)
