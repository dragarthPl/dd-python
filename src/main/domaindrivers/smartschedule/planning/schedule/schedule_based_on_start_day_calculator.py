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
        current_start: datetime = start_date
        all_sorted: list[ParallelStages] = parallelized_stages.all_sorted(comparing)
        for stages in all_sorted:
            parallelized_stages_end: datetime = current_start
            for stage in stages.stages:
                stage_end: datetime = current_start + stage.duration
                schedule_map[stage.stage_name] = TimeSlot(current_start, stage_end)
                if stage_end > parallelized_stages_end:
                    parallelized_stages_end = stage_end
            current_start = parallelized_stages_end
        return schedule_map
