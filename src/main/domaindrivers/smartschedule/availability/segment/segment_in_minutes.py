from attr import frozen
from domaindrivers.smartschedule.availability.segment.segments import Segments


@frozen
class SegmentInMinutes:
    value: int

    @classmethod
    def of(cls, minutes: int) -> "SegmentInMinutes":
        if minutes <= 0:
            raise ValueError("SegmentInMinutesDuration must be positive")
        if minutes % Segments.DEFAULT_SEGMENT_DURATION_IN_MINUTES != 0:
            raise ValueError("SegmentInMinutesDuration must be a multiple of 15")
        return SegmentInMinutes(minutes)

    @classmethod
    def default_segment(cls) -> "SegmentInMinutes":
        return cls.of(Segments.DEFAULT_SEGMENT_DURATION_IN_MINUTES)
