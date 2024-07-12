from datetime import datetime

from attr import frozen
from domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.schedule.calendars import Calendars
from domaindrivers.smartschedule.planning.schedule.schedule_based_on_chosen_resources_availability_calculator import (
    ScheduleBasedOnChosenResourcesAvailabilityCalculator,
)
from domaindrivers.smartschedule.planning.schedule.schedule_based_on_reference_stage_calculator import (
    ScheduleBasedOnReferenceStageCalculator,
)
from domaindrivers.smartschedule.planning.schedule.schedule_based_on_start_day_calculator import (
    ScheduleBasedOnStartDayCalculator,
)
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class Schedule:
    dates: dict[str, TimeSlot]

    @classmethod
    def none(cls) -> "Schedule":
        return Schedule({})

    @classmethod
    def based_on_start_day(cls, start_date: datetime, parallelized_stages: ParallelStagesList) -> "Schedule":
        schedule_map: dict[str, TimeSlot] = ScheduleBasedOnStartDayCalculator().calculate(
            start_date,
            parallelized_stages,
            lambda parallel_stages_a, parallel_stages_b: (parallel_stages_a.print() > parallel_stages_b.print())
            - (parallel_stages_a.print() < parallel_stages_b.print()),
        )
        return cls(schedule_map)

    @classmethod
    def based_on_reference_stage_time_slot(
        cls, reference_stage: Stage, stage_proposed_time_slot: TimeSlot, parallelized_stages: ParallelStagesList
    ) -> "Schedule":
        schedule_map: dict[str, TimeSlot] = ScheduleBasedOnReferenceStageCalculator().calculate(
            reference_stage,
            stage_proposed_time_slot,
            parallelized_stages,
            lambda parallel_stages_a, parallel_stages_b: (parallel_stages_a.print() > parallel_stages_b.print())
            - (parallel_stages_a.print() < parallel_stages_b.print()),
        )
        return cls(schedule_map)

    @classmethod
    def based_on_chosen_resources_availability(
        cls, chosen_resources_calendars: Calendars, stages: list[Stage]
    ) -> "Schedule":
        schedule: dict[str, TimeSlot] = ScheduleBasedOnChosenResourcesAvailabilityCalculator().calculate(
            chosen_resources_calendars, stages
        )
        return cls(schedule)
