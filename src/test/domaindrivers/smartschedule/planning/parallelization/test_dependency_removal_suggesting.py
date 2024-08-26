from typing import Final
from unittest import TestCase

from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.parallelization.stage_parallelization import (
    RemovalSuggestion,
    StageParallelization,
)


class TestDependencyRemovalSuggesting(TestCase):
    stage_parallelization: Final[StageParallelization] = StageParallelization()

    def test_suggesting_breaks_the_cycle_in_schedule(self) -> None:
        # given
        stage1: Stage = Stage.from_name("Stage1")
        stage2: Stage = Stage.from_name("Stage2")
        stage3: Stage = Stage.from_name("Stage3")
        stage4: Stage = Stage.from_name("Stage4")
        stage1 = stage1.depends_on(stage2)
        stage2 = stage2.depends_on(stage3)
        stage4 = stage4.depends_on(stage3)
        stage1 = stage1.depends_on(stage4)
        stage3 = stage3.depends_on(stage1)

        # when
        suggestion: RemovalSuggestion = self.stage_parallelization.what_to_remove({stage1, stage2, stage3, stage4})

        # then
        self.assertEqual(suggestion.to_string(), "['(3 -> 4)', '(4 -> 1)']")
