from datetime import timedelta
from typing import Final
from unittest import TestCase

from domaindrivers.smartschedule.planning.parallelization.duration_calculator import DurationCalculator
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.utils.duration import ZERO


class TestDurationCalculator(TestCase):
    __duration_calculator: Final[DurationCalculator] = DurationCalculator()

    def test_longest_stage_is_taken_into_account(self) -> None:
        # given
        stage1: Stage = Stage.from_name("Stage1").of_duration(ZERO)
        stage2: Stage = Stage.from_name("Stage2").of_duration(timedelta(days=3))
        stage3: Stage = Stage.from_name("Stage3").of_duration(timedelta(days=2))
        stage4: Stage = Stage.from_name("Stage4").of_duration(timedelta(days=5))

        # when
        duration: timedelta = self.__duration_calculator.apply([stage1, stage2, stage3, stage4])

        # then
        self.assertEqual(duration, timedelta(days=5))

    def test_sum_is_taken_into_account_when_nothing_is_parallel(self) -> None:
        # given
        stage1: Stage = Stage.from_name("stage_1").of_duration(timedelta(hours=10))
        stage2: Stage = Stage.from_name("stage_2").of_duration(timedelta(hours=24))
        stage3: Stage = Stage.from_name("stage_3").of_duration(timedelta(days=2))
        stage4: Stage = Stage.from_name("stage_4").of_duration(timedelta(days=1))
        stage4.depends_on(stage3)
        stage3.depends_on(stage2)
        stage2.depends_on(stage1)

        # when
        duration: timedelta = self.__duration_calculator.apply([stage1, stage2, stage3, stage4])

        # then
        self.assertEqual(duration, timedelta(hours=106))
