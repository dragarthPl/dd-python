from typing import Final
from unittest import TestCase

from domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.parallelization.stage_parallelization import StageParallelization


class TestParallelization(TestCase):
    stage_parallelization: Final[StageParallelization] = StageParallelization()

    def test_parallelization(self) -> None:
        # given
        stage1: Stage = Stage.from_name("Stage1")
        stage2: Stage = Stage.from_name("Stage2")

        # when
        sorted_stages: ParallelStagesList = self.stage_parallelization.of({stage1, stage2})

        # then
        self.assertEqual(1, len(sorted_stages.all))

    def test_simple_dependencies(self) -> None:
        # given
        stage1: Stage = Stage.from_name("Stage1")
        stage2: Stage = Stage.from_name("Stage2")
        stage3: Stage = Stage.from_name("Stage3")
        stage4: Stage = Stage.from_name("Stage4")
        stage2.depends_on(stage1)
        stage3.depends_on(stage1)
        stage4.depends_on(stage2)

        # when
        sorted_stages: ParallelStagesList = self.stage_parallelization.of({stage1, stage2, stage3, stage4})

        # then
        self.assertEqual(sorted_stages.print(), "Stage1 | Stage2, Stage3 | Stage4")

    def test_cant_be_done_when_there_is_acycle(self) -> None:
        # given
        stage1: Stage = Stage.from_name("Stage1")
        stage2: Stage = Stage.from_name("Stage2")
        stage2.depends_on(stage1)
        stage1.depends_on(stage2)  # making it cyclic

        # when
        sorted_stages: ParallelStagesList = self.stage_parallelization.of({stage1, stage2})

        # then
        self.assertTrue(sorted_stages.all == [])
