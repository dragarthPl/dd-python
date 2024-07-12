from datetime import datetime, timedelta
from typing import Callable

from domaindrivers.smartschedule.planning.parallelization.parallel_stages import ParallelStages
from domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class ScheduleBasedOnReferenceStageCalculator:
    def calculate(
        self,
        reference_stage: Stage,
        reference_stage_proposed_time_slot: TimeSlot,
        parallelized_stages: ParallelStagesList,
        comparing: Callable[[ParallelStages, ParallelStages], int],
    ) -> dict[str, TimeSlot]:
        all: list[ParallelStages] = parallelized_stages.all_sorted(comparing)
        reference_stage_index: int = self.__find_reference_stage_index(reference_stage, all)
        if reference_stage_index == -1:
            return {}
        schedule_map: dict[str, TimeSlot] = {}
        stages_before_reference: list[ParallelStages] = all[0:reference_stage_index]
        stages_after_reference: list[ParallelStages] = all[reference_stage_index + 1 : len(all)]
        self.__calculate_stages_before_critical(
            stages_before_reference, reference_stage_proposed_time_slot, schedule_map
        )
        self.__calculate_stages_after_critical(stages_after_reference, reference_stage_proposed_time_slot, schedule_map)
        self.__calculate_stages_with_reference_stage(
            all[reference_stage_index], reference_stage_proposed_time_slot, schedule_map
        )
        return schedule_map

    def __calculate_stages_before_critical(
        self, before: list[ParallelStages], stage_proposed_time_slot: TimeSlot, schedule_map: dict[str, TimeSlot]
    ) -> dict[str, TimeSlot]:
        current_start: datetime = stage_proposed_time_slot.since
        for parallel_stages in reversed(before):
            current_stages: ParallelStages = parallel_stages
            stage_duration: timedelta = current_stages.duration()
            start: datetime = current_start - stage_duration
            for stage in current_stages.stages:
                schedule_map[stage.stage_name] = TimeSlot(start, start + stage.duration)
        return schedule_map

    def __calculate_stages_after_critical(
        self, after: list[ParallelStages], stage_proposed_time_slot: TimeSlot, schedule_map: dict[str, TimeSlot]
    ) -> dict[str, TimeSlot]:
        current_start: datetime = stage_proposed_time_slot.to
        for current_stages in after:
            for stage in current_stages.stages:
                schedule_map[stage.stage_name] = TimeSlot(current_start, current_start + stage.duration)
            current_start = current_start + current_stages.duration()
        return schedule_map

    def __calculate_stages_with_reference_stage(
        self,
        stages_with_reference: ParallelStages,
        stage_proposed_time_slot: TimeSlot,
        schedule_map: dict[str, TimeSlot],
    ) -> dict[str, TimeSlot]:
        current_start: datetime = stage_proposed_time_slot.since
        for stage in stages_with_reference.stages:
            schedule_map[stage.stage_name] = TimeSlot(current_start, current_start + stage.duration)
        return schedule_map

    def __find_reference_stage_index(self, reference_stage: Stage, all: list[ParallelStages]) -> int:
        stages_with_the_reference_stage_with_proposed_time_index: int = -1
        for i, parallel_stages in enumerate(all):
            stages: ParallelStages = parallel_stages
            stages_names: set[str] = set(map(lambda stage: stage.stage_name, stages.stages))
            if reference_stage.stage_name in stages_names:
                stages_with_the_reference_stage_with_proposed_time_index = i
                break
        return stages_with_the_reference_stage_with_proposed_time_index
