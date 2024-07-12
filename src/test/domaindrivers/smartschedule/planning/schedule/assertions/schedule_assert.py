from typing import Any
from unittest import TestCase

from domaindrivers.smartschedule.planning.schedule.schedule import Schedule
from domaindrivers.smartschedule.planning.schedule.time_slot import TimeSlot

from .stage_assert import StageAssert


class ScheduleAssert(TestCase):
    actual: Schedule

    def __init__(self, actual: Schedule, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.actual = actual

    @classmethod
    def assertThat(cls, actual: Schedule) -> "ScheduleAssert":
        return cls(actual)

    def hasStagesInt(self, number: int) -> "ScheduleAssert":
        self.assertEqual(len(self.actual.dates.keys()), number)
        return self

    def hasStageStr(self, name: str) -> "StageAssert":
        stage_time_slot: TimeSlot = self.actual.dates.get(name)
        self.assertIsNotNone(stage_time_slot)
        return StageAssert(stage_time_slot, self)

    def isEmpty(self) -> None:
        self.assertEqual(self.actual, Schedule.none())

    def schedule(self) -> Schedule:
        return self.actual
