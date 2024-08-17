from datetime import datetime
from typing import Final
from unittest import TestCase

from domaindrivers.smartschedule.availability.segment.segment_in_minutes import SegmentInMinutes
from domaindrivers.smartschedule.availability.segment.slot_to_normalized_slot import SlotToNormalizedSlot
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestSlotToNormalizedSlot(TestCase):
    SLOT_TO_NORMALIZED_SLOT: Final[SlotToNormalizedSlot] = SlotToNormalizedSlot()

    def test_has_no_effect_when_slot_already_normalized(self) -> None:
        # given
        start: datetime = datetime.strptime("2023-09-09T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        end: datetime = datetime.strptime("2023-09-09T01:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        time_slot: TimeSlot = TimeSlot(start, end)
        one_hour: SegmentInMinutes = SegmentInMinutes.of(60)

        # when
        normalized: TimeSlot = SlotToNormalizedSlot().apply(time_slot, one_hour)

        # then
        self.assertEqual(time_slot, normalized)

    def test_normalized_to_the_hour(self) -> None:
        # given
        start: datetime = datetime.strptime("2023-09-09T00:10:00Z", "%Y-%m-%dT%H:%M:%SZ")
        end: datetime = datetime.strptime("2023-09-09T00:59:00Z", "%Y-%m-%dT%H:%M:%SZ")
        time_slot: TimeSlot = TimeSlot(start, end)
        one_hour: SegmentInMinutes = SegmentInMinutes.of(60)

        # when
        normalized: TimeSlot = self.SLOT_TO_NORMALIZED_SLOT.apply(time_slot, one_hour)

        # then
        self.assertEqual(datetime.strptime("2023-09-09T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), normalized.since)
        self.assertEqual(datetime.strptime("2023-09-09T01:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), normalized.to)

    def test_normalized_when_short_slot_overlapping_two_segments(self) -> None:
        # given
        start: datetime = datetime.strptime("2023-09-09T00:29:00Z", "%Y-%m-%dT%H:%M:%SZ")
        end: datetime = datetime.strptime("2023-09-09T00:31:00Z", "%Y-%m-%dT%H:%M:%SZ")
        time_slot: TimeSlot = TimeSlot(start, end)
        one_hour: SegmentInMinutes = SegmentInMinutes.of(60)

        # when
        normalized: TimeSlot = self.SLOT_TO_NORMALIZED_SLOT.apply(time_slot, one_hour)

        # then
        self.assertEqual(datetime.strptime("2023-09-09T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), normalized.since)
        self.assertEqual(datetime.strptime("2023-09-09T01:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), normalized.to)

    def test_no_normalization_when_slot_starts_at_segment_start(self) -> None:
        # given
        start: datetime = datetime.strptime("2023-09-09T00:15:00Z", "%Y-%m-%dT%H:%M:%SZ")
        end: datetime = datetime.strptime("2023-09-09T00:30:00Z", "%Y-%m-%dT%H:%M:%SZ")
        time_slot: TimeSlot = TimeSlot(start, end)
        start2: datetime = datetime.strptime("2023-09-09T00:30:00Z", "%Y-%m-%dT%H:%M:%SZ")
        end2: datetime = datetime.strptime("2023-09-09T00:45:00Z", "%Y-%m-%dT%H:%M:%SZ")
        time_slot_2: TimeSlot = TimeSlot(start2, end2)
        fifteen_minutes: SegmentInMinutes = SegmentInMinutes.of(15)

        # when
        normalized: TimeSlot = self.SLOT_TO_NORMALIZED_SLOT.apply(time_slot, fifteen_minutes)
        normalized_2: TimeSlot = self.SLOT_TO_NORMALIZED_SLOT.apply(time_slot_2, fifteen_minutes)

        # then
        self.assertEqual(datetime.strptime("2023-09-09T00:15:00Z", "%Y-%m-%dT%H:%M:%SZ"), normalized.since)
        self.assertEqual(datetime.strptime("2023-09-09T00:30:00Z", "%Y-%m-%dT%H:%M:%SZ"), normalized.to)
        self.assertEqual(datetime.strptime("2023-09-09T00:30:00Z", "%Y-%m-%dT%H:%M:%SZ"), normalized_2.since)
        self.assertEqual(datetime.strptime("2023-09-09T00:45:00Z", "%Y-%m-%dT%H:%M:%SZ"), normalized_2.to)
