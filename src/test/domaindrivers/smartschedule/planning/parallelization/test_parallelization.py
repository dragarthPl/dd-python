from typing import Final
from unittest import TestCase

from domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from domaindrivers.smartschedule.planning.parallelization.stage import ResourceName, Stage
from domaindrivers.smartschedule.planning.parallelization.stage_parallelization import StageParallelization


class TestParallelization(TestCase):
    stage_parallelization: Final[StageParallelization] = StageParallelization()

    LEON: Final[ResourceName] = ResourceName("Leon")
    ERYK: Final[ResourceName] = ResourceName("Eric")
    SLAWEK: Final[ResourceName] = ResourceName("Sławek")
    KUBA: Final[ResourceName] = ResourceName("Kuba")

    def test_everything_can_be_done_in_parallel_when_there_are_no_dependencies(self) -> None:
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
        stage2 = stage2.depends_on(stage1)
        stage3 = stage3.depends_on(stage1)
        stage4 = stage4.depends_on(stage2)

        # when
        sorted_stages: ParallelStagesList = self.stage_parallelization.of({stage1, stage2, stage3, stage4})

        # then
        self.assertEqual(sorted_stages.print(), "Stage1 | Stage2, Stage3 | Stage4")

    def test_cant_be_done_when_there_is_acycle(self) -> None:
        # given
        stage1: Stage = Stage.from_name("Stage1")
        stage2: Stage = Stage.from_name("Stage2")
        stage2 = stage2.depends_on(stage1)
        stage1 = stage1.depends_on(stage2)  # making it cyclic

        # when
        sorted_stages: ParallelStagesList = self.stage_parallelization.of({stage1, stage2})

        # then
        self.assertTrue(sorted_stages.all == [])

    def test_takes_into_account_shared_resources(self) -> None:
        # given
        stage1: Stage = Stage.from_name("Stage1").with_chosen_resource_capabilities(self.LEON)
        stage2: Stage = Stage.from_name("Stage2").with_chosen_resource_capabilities(self.ERYK, self.LEON)
        stage3: Stage = Stage.from_name("Stage3").with_chosen_resource_capabilities(self.SLAWEK)
        stage4: Stage = Stage.from_name("Stage4").with_chosen_resource_capabilities(self.SLAWEK, self.KUBA)

        # when
        parallel_stages: ParallelStagesList = self.stage_parallelization.of({stage1, stage2, stage3, stage4})

        # then
        self.assertTrue(
            parallel_stages.print() in ("Stage1, Stage3 | Stage2, Stage4", "Stage2, Stage4 | Stage1, Stage3")
        )
