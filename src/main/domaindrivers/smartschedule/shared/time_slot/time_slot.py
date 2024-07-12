from __future__ import annotations

from datetime import datetime, timedelta

import pytz
from attr import frozen
from dateutil.relativedelta import relativedelta


@frozen
class TimeSlot:
    since: datetime
    to: datetime

    @classmethod
    def empty(cls) -> "TimeSlot":
        return cls(datetime.min, datetime.min)

    @classmethod
    def create_daily_time_slot_at_utc(cls, year: int, month: int, day: int) -> "TimeSlot":
        this_day = datetime(year, month, day)
        since = this_day.astimezone(pytz.utc)
        return cls(since, since + relativedelta(days=1))

    @classmethod
    def create_monthly_time_slot_at_utc(cls, year: int, month: int) -> "TimeSlot":
        start_of_month: datetime = datetime(year, month, 1)
        end_of_month: datetime = start_of_month + relativedelta(months=1)
        since = start_of_month.astimezone(pytz.utc)
        to = end_of_month.astimezone(pytz.utc)
        return TimeSlot(since, to)

    def overlaps_with(self, other: TimeSlot) -> bool:
        return not self.since > other.to and not self.to < other.since

    def within(self, other: TimeSlot) -> bool:
        return not self.since < other.since and not self.to > other.to

    def leftover_after_removing_common_with(self, other: TimeSlot) -> list[TimeSlot]:
        result: list[TimeSlot] = []
        if other == self:
            return []
        if not other.overlaps_with(self):
            return [self, other]
        if self == other:
            return result
        if self.since < other.since:
            result.append(TimeSlot(self.since, other.since))
        if other.since < self.since:
            result.append(TimeSlot(other.since, self.since))
        if self.to > other.to:
            result.append(TimeSlot(other.to, self.to))
        if other.to > self.to:
            result.append(TimeSlot(self.to, other.to))
        return result

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
