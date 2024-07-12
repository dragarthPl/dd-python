from datetime import datetime
from typing import Callable

from domaindrivers.smartschedule.planning.parallelization.parallel_stages import ParallelStages
from domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class ScheduleBasedOnStartDayCalculator:
    def calculate(
        self,
        start_date: datetime,
        parallelized_stages: ParallelStagesList,
        comparing: Callable[[ParallelStages, ParallelStages], int],
    ) -> dict[str, TimeSlot]:
        schedule_map: dict[str, TimeSlot] = {}
        current_start: datetime = start_date  # noqa: F841
        all_sorted: list[ParallelStages] = parallelized_stages.all_sorted(comparing)  # noqa: F841
        # TODO
        return schedule_map
