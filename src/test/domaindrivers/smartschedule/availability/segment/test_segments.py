from datetime import datetime
from unittest import TestCase

from domaindrivers.smartschedule.availability.segment.segment_in_minutes import SegmentInMinutes
from domaindrivers.smartschedule.availability.segment.segments import Segments
from domaindrivers.smartschedule.availability.segment.slot_to_segments import SlotToSegments
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestSegments(TestCase):
    def test_unit_has_to_be_multiple_of_15_minutes(self) -> None:
        # expect
        with self.assertRaises(ValueError):
            SegmentInMinutes.of(20)
        with self.assertRaises(ValueError):
            SegmentInMinutes.of(18)
        with self.assertRaises(ValueError):
            SegmentInMinutes.of(7)
        self.assertIsNotNone(SegmentInMinutes.of(15))
        self.assertIsNotNone(SegmentInMinutes.of(30))
        self.assertIsNotNone(SegmentInMinutes.of(45))

    def test_splitting_into_segments_when_there_is_no_leftover(self) -> None:
        # given
        start: datetime = datetime.strptime("2023-09-09T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        end: datetime = datetime.strptime("2023-09-09T01:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        time_slot: TimeSlot = TimeSlot(start, end)

        # when
        segments: list[TimeSlot] = Segments.split(time_slot, SegmentInMinutes.of(15))

        # then
        self.assertEqual(4, len(segments))
        self.assertEqual(datetime.strptime("2023-09-09T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), segments[0].since)
        self.assertEqual(datetime.strptime("2023-09-09T00:15:00Z", "%Y-%m-%dT%H:%M:%SZ"), segments[0].to)
        self.assertEqual(datetime.strptime("2023-09-09T00:15:00Z", "%Y-%m-%dT%H:%M:%SZ"), segments[1].since)
        self.assertEqual(datetime.strptime("2023-09-09T00:30:00Z", "%Y-%m-%dT%H:%M:%SZ"), segments[1].to)
        self.assertEqual(datetime.strptime("2023-09-09T00:30:00Z", "%Y-%m-%dT%H:%M:%SZ"), segments[2].since)
        self.assertEqual(datetime.strptime("2023-09-09T00:45:00Z", "%Y-%m-%dT%H:%M:%SZ"), segments[2].to)
        self.assertEqual(datetime.strptime("2023-09-09T00:45:00Z", "%Y-%m-%dT%H:%M:%SZ"), segments[3].since)
        self.assertEqual(datetime.strptime("2023-09-09T01:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), segments[3].to)

    def test_splitting_into_segments_just_normalizes_if_chosen_segment_larger_than_passed_slot(self) -> None:
        # given
        start: datetime = datetime.strptime("2023-09-09T00:10:00Z", "%Y-%m-%dT%H:%M:%SZ")
        end: datetime = datetime.strptime("2023-09-09T01:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        time_slot: TimeSlot = TimeSlot(start, end)

        # when
        segments: list[TimeSlot] = Segments.split(time_slot, SegmentInMinutes.of(90))

        # then
        self.assertEqual(1, len(segments))
        self.assertEqual(datetime.strptime("2023-09-09T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), segments[0].since)
        self.assertEqual(datetime.strptime("2023-09-09T01:30:00Z", "%Y-%m-%dT%H:%M:%SZ"), segments[0].to)

    def test_normalizing_atime_slot(self) -> None:
        # given
        start: datetime = datetime.strptime("2023-09-09T00:10:00Z", "%Y-%m-%dT%H:%M:%SZ")
        end: datetime = datetime.strptime("2023-09-09T01:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        time_slot: TimeSlot = TimeSlot(start, end)

        # when
        segment: TimeSlot = Segments.normalize_to_segment_boundaries(time_slot, SegmentInMinutes.of(90))

        # then
        self.assertEqual(datetime.strptime("2023-09-09T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), segment.since)
        self.assertEqual(datetime.strptime("2023-09-09T01:30:00Z", "%Y-%m-%dT%H:%M:%SZ"), segment.to)

    def test_slots_are_normalized_before_splitting(self) -> None:
        # given
        start: datetime = datetime.strptime("2023-09-09T00:10:00Z", "%Y-%m-%dT%H:%M:%SZ")
        end: datetime = datetime.strptime("2023-09-09T00:59:00Z", "%Y-%m-%dT%H:%M:%SZ")
        time_slot: TimeSlot = TimeSlot(start, end)
        one_hour: SegmentInMinutes = SegmentInMinutes.of(60)

        # when
        segments: list[TimeSlot] = Segments.split(time_slot, one_hour)

        # then
        self.assertEqual(1, len(segments))
        self.assertEqual(datetime.strptime("2023-09-09T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), segments[0].since)
        self.assertEqual(datetime.strptime("2023-09-09T01:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), segments[0].to)

    def test_splitting_into_segments_without_normalization(self) -> None:
        # given
        start: datetime = datetime.strptime("2023-09-09T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        end: datetime = datetime.strptime("2023-09-09T00:59:00Z", "%Y-%m-%dT%H:%M:%SZ")
        time_slot: TimeSlot = TimeSlot(start, end)

        # when
        segments: list[TimeSlot] = SlotToSegments().apply(time_slot, SegmentInMinutes.of(30))

        # then
        self.assertEqual(2, len(segments))

        self.assertEqual(datetime.strptime("2023-09-09T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"), segments[0].since)
        self.assertEqual(datetime.strptime("2023-09-09T00:30:00Z", "%Y-%m-%dT%H:%M:%SZ"), segments[0].to)
        self.assertEqual(datetime.strptime("2023-09-09T00:30:00Z", "%Y-%m-%dT%H:%M:%SZ"), segments[1].since)
        self.assertEqual(datetime.strptime("2023-09-09T00:59:00Z", "%Y-%m-%dT%H:%M:%SZ"), segments[1].to)
