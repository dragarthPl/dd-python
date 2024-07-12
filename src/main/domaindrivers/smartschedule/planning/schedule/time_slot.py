from __future__ import annotations

from datetime import datetime, timedelta

from attr import frozen


@frozen
class TimeSlot:
    since: datetime
    to: datetime

    @classmethod
    def empty(cls) -> "TimeSlot":
        return cls(datetime.min, datetime.min)

    def overlaps_with(self, other: TimeSlot) -> bool:
        return not self.since > other.to and not self.to < other.since

    def within(self, other: TimeSlot) -> bool:
        return not self.since < other.since and not self.to > other.to

    def common_part_with(self, other: TimeSlot) -> TimeSlot:
        if not self.overlaps_with(other):
            return TimeSlot.empty()
        common_start: datetime = self.since if self.since > other.since else other.since
        common_end: datetime = self.to if self.to < other.to else other.to
        return TimeSlot(common_start, common_end)

    def is_empty(self) -> bool:
        return self.since == self.to

    def duration(self) -> timedelta:
        return self.to - self.since

    def stretch(self, duration: timedelta) -> TimeSlot:
        return TimeSlot(self.since - duration, self.to + duration)
