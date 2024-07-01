from __future__ import annotations

from datetime import datetime

import pytz
from attr import frozen
from dateutil.relativedelta import relativedelta


@frozen
class TimeSlot:
    since: datetime
    to: datetime

    @classmethod
    def create_daily_time_slot_at_utc(cls, year: int, month: int, day: int) -> "TimeSlot":
        this_day = datetime(year, month, day)
        since = this_day.astimezone(pytz.utc)
        return cls(since, since + relativedelta(days=1))

    def within(self, other: TimeSlot) -> bool:
        return not self.since > other.since and not self.to < other.to
