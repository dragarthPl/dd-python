from __future__ import annotations

from typing import Final

from domaindrivers.smartschedule.availability.segment.slot_to_normalized_slot import SlotToNormalizedSlot
from domaindrivers.smartschedule.availability.segment.slot_to_segments import SlotToSegments
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class Segments:
    DEFAULT_SEGMENT_DURATION_IN_MINUTES: Final[int] = 15

    @classmethod
    def split(cls, time_slot: TimeSlot, unit: "SegmentInMinutes") -> list[TimeSlot]:  # type: ignore # noqa: F821
        normalized_slot: TimeSlot = cls.normalize_to_segment_boundaries(time_slot, unit)
        return SlotToSegments().apply(normalized_slot, unit)

    @classmethod
    def normalize_to_segment_boundaries(cls, time_slot: TimeSlot, unit: "SegmentInMinutes") -> TimeSlot:  # type: ignore # noqa: F821
        return SlotToNormalizedSlot().apply(time_slot, unit)
