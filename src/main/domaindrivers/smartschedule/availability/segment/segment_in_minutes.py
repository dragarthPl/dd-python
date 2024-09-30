from attr import frozen
from domaindrivers.smartschedule.availability.segment.segments import Segments


@frozen
class SegmentInMinutes:
    value: int

    @classmethod
    def of_duration(cls, minutes: int, slot_duration_in_minutes: int) -> "SegmentInMinutes":
        if minutes <= 0:
            raise ValueError("SegmentInMinutesDuration must be positive")
        if minutes < slot_duration_in_minutes:
            raise ValueError(f"SegmentInMinutesDuration must be at least {slot_duration_in_minutes} minutes")
        if minutes % slot_duration_in_minutes != 0:
            raise ValueError(f"SegmentInMinutesDuration must be a multiple of {slot_duration_in_minutes} minutes")
        return SegmentInMinutes(minutes)

    @classmethod
    def of(cls, minutes: int) -> "SegmentInMinutes":
        return cls.of_duration(minutes, Segments.DEFAULT_SEGMENT_DURATION_IN_MINUTES)

    @classmethod
    def default_segment(cls) -> "SegmentInMinutes":
        return cls.of(Segments.DEFAULT_SEGMENT_DURATION_IN_MINUTES)
