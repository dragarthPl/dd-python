from __future__ import annotations

from datetime import datetime, timedelta

from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.utils.functional import BiFunction


class SlotToNormalizedSlot(BiFunction[TimeSlot, "SegmentInMinutes", TimeSlot]):  # type: ignore
    def apply(self, time_slot: TimeSlot, segment_in_minutes: "SegmentInMinutes") -> TimeSlot:  # type: ignore # noqa: F821
        segment_in_minutes_duration: int = segment_in_minutes.value
        segment_start: datetime = self.__normalize_start(time_slot.since, segment_in_minutes_duration)
        segment_end: datetime = self.__normalize_end(time_slot.to, segment_in_minutes_duration)
        normalized: TimeSlot = TimeSlot(segment_start, segment_end)
        minimal_segment: TimeSlot = TimeSlot(segment_start, segment_start + timedelta(minutes=segment_in_minutes.value))
        if normalized.within(minimal_segment):
            return minimal_segment
        return normalized

    def __normalize_end(self, initial_end: datetime, segment_in_minutes_duration: int) -> datetime:
        closest_segment_end: datetime = initial_end.replace(minute=0, second=0, microsecond=0)
        while initial_end > closest_segment_end:
            closest_segment_end = closest_segment_end + timedelta(minutes=segment_in_minutes_duration)
        return closest_segment_end

    def __normalize_start(self, initial_start: datetime, segment_in_minutes_duration: int) -> datetime:
        closest_segment_start: datetime = initial_start.replace(minute=0, second=0, microsecond=0)
        if closest_segment_start + timedelta(minutes=segment_in_minutes_duration) > initial_start:
            return closest_segment_start
        while closest_segment_start < initial_start:
            closest_segment_start = closest_segment_start + timedelta(minutes=segment_in_minutes_duration)
        return closest_segment_start
