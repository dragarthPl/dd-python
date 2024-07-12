from __future__ import annotations

from datetime import datetime
from typing import Final, TYPE_CHECKING
from unittest import TestCase

if TYPE_CHECKING:
    from .schedule_assert import ScheduleAssert

from domaindrivers.smartschedule.planning.schedule.schedule import Schedule
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class StageAssert(TestCase):
    actual: TimeSlot
    schedule_assert: Final["ScheduleAssert"]

    def __init__(self, actual: TimeSlot, schedule_assert: ScheduleAssert = None) -> None:
        super().__init__()
        self.actual = actual
        self.schedule_assert = schedule_assert

    def thatStarts(self, start: str) -> "StageAssert":
        self.assertEqual(self.actual.since, datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ"))
        return self

    def withSlot(self, slot: TimeSlot) -> "StageAssert":
        self.assertEqual(self.actual, slot)
        return self

    def thatEnds(self, end: str) -> "StageAssert":
        self.assertEqual(self.actual.since, datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ"))
        return self

    def and_(self) -> ScheduleAssert:
        return self.schedule_assert

    def isBefore(self, stage: str) -> "StageAssert":
        schedule: Schedule = self.schedule_assert.schedule()
        self.assertLessEqual(self.actual.to, schedule.dates.get(stage).since)
        return self

    def startsTogetherWith(self, stage: str) -> "StageAssert":
        schedule: Schedule = self.schedule_assert.schedule()
        self.assertLessEqual(self.actual.since, schedule.dates.get(stage).since)
        return self

    def isAfter(self, stage: str) -> "StageAssert":
        schedule: Schedule = self.schedule_assert.schedule()
        self.assertLessEqual(self.actual.since, schedule.dates.get(stage).to)
        return self
