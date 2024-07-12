from datetime import datetime, timedelta
from typing import Final
from unittest import TestCase

from domaindrivers.smartschedule.planning.parallelization.parallel_stages import ParallelStages
from domaindrivers.smartschedule.planning.parallelization.parallel_stages_list import ParallelStagesList
from domaindrivers.smartschedule.planning.parallelization.resource_name import ResourceName
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.schedule.calendars import Calendar, Calendars
from domaindrivers.smartschedule.planning.schedule.schedule import Schedule
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot

from .assertions.schedule_assert import ScheduleAssert


class TestScheduleCalculation(TestCase):
    JAN_1: datetime = datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    JAN_10_20: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-20T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    JAN_1_1: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-02T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    JAN_3_10: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-10T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    JAN_1_20: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-20T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    JAN_11_21: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-11T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-21T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    JAN_1_4: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-04T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    JAN_4_14: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-04T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-14T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    JAN_14_16: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-14T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-16T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    JAN_1_5: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-05T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    DEC_29_JAN_1: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2019-12-29T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    JAN_1_11: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-11T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    JAN_5_7: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-05T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-07T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )
    JAN_3_6: Final[TimeSlot] = TimeSlot(
        datetime.strptime("2020-01-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        datetime.strptime("2020-01-06T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
    )

    def test_can_calculate_schedule_based_on_the_start_day(self) -> None:
        # given
        stage_1: Stage = Stage.from_name("Stage1").of_duration(timedelta(days=3))
        stage_2: Stage = Stage.from_name("Stage2").of_duration(timedelta(days=10))
        stage_3: Stage = Stage.from_name("Stage3").of_duration(timedelta(days=2))
        # and
        parallel_stages: ParallelStagesList = ParallelStagesList.of(
            ParallelStages.of(stage_1), ParallelStages.of(stage_2), ParallelStages.of(stage_3)
        )

        # when
        schedule: Schedule = Schedule.based_on_start_day(self.JAN_1, parallel_stages)

        # then
        (
            ScheduleAssert(schedule)
            .hasStage("Stage1")
            .withSlot(self.JAN_1_4)
            .and_()
            .hasStage("Stage2")
            .withSlot(self.JAN_4_14)
            .and_()
            .hasStage("Stage3")
            .withSlot(self.JAN_14_16)
        )

    def test_schedule_can_adjust_to_dates_of_one_reference_stage(self) -> None:
        # given
        stage: Stage = Stage.from_name("S1").of_duration(timedelta(days=3))
        another_stage: Stage = Stage.from_name("S2").of_duration(timedelta(days=10))
        yet_another_stage: Stage = Stage.from_name("S3").of_duration(timedelta(days=2))
        reference_stage: Stage = Stage.from_name("S4-Reference").of_duration(timedelta(days=4))
        # and
        parallel_stages: ParallelStagesList = ParallelStagesList.of(
            ParallelStages.of(stage),
            ParallelStages.of(reference_stage, another_stage),
            ParallelStages.of(yet_another_stage),
        )

        # when
        schedule: Schedule = Schedule.based_on_reference_stage_time_slot(reference_stage, self.JAN_1_5, parallel_stages)

        # then
        (
            ScheduleAssert(schedule)
            .hasStage("S1")
            .withSlot(self.DEC_29_JAN_1)
            .isBefore("S4-Reference")
            .and_()
            .hasStage("S2")
            .withSlot(self.JAN_1_11)
            .startsTogetherWith("S4-Reference")
            .and_()
            .hasStage("S3")
            .withSlot(self.JAN_5_7)
            .isAfter("S4-Reference")
            .and_()
            .hasStage("S4-Reference")
            .withSlot(self.JAN_1_5)
        )

    def test_no_schedule_is_calculated_if_reference_stage_to_adjust_to_does_not_exists(self) -> None:
        # given
        stage_1: Stage = Stage.from_name("Stage1").of_duration(timedelta(days=3))
        stage_2: Stage = Stage.from_name("Stage2").of_duration(timedelta(days=10))
        stage_3: Stage = Stage.from_name("Stage3").of_duration(timedelta(days=2))
        stage_4: Stage = Stage.from_name("Stage4").of_duration(timedelta(days=4))
        # and
        parallel_stages: ParallelStagesList = ParallelStagesList.of(
            ParallelStages.of(stage_1), ParallelStages.of(stage_2, stage_4), ParallelStages.of(stage_3)
        )

        # when
        schedule: Schedule = Schedule.based_on_reference_stage_time_slot(
            Stage.from_name("Stage5"), self.JAN_1_5, parallel_stages
        )

        # then
        ScheduleAssert(schedule).isEmpty()

    def test_can_adjust_schedule_to_availability_of_needed_resources(self) -> None:
        # given
        r1: ResourceName = ResourceName("r1")
        r2: ResourceName = ResourceName("r2")
        r3: ResourceName = ResourceName("r3")
        # and
        stage_1: Stage = Stage.from_name("Stage1").of_duration(timedelta(days=3)).with_chosen_resource_capabilities(r1)
        stage_2: Stage = (
            Stage.from_name("Stage2").of_duration(timedelta(days=10)).with_chosen_resource_capabilities(r2, r3)
        )
        # and
        cal1: Calendar = Calendar.with_available_slots(r1, self.JAN_1_1, self.JAN_3_10)
        cal2: Calendar = Calendar.with_available_slots(r2, self.JAN_1_20)
        cal3: Calendar = Calendar.with_available_slots(r3, self.JAN_11_21)

        # when
        schedule: Schedule = Schedule.based_on_chosen_resources_availability(
            Calendars.of(cal1, cal2, cal3), [stage_1, stage_2]
        )

        # then
        (
            ScheduleAssert(schedule)
            .hasStage("Stage1")
            .withSlot(self.JAN_3_6)
            .and_()
            .hasStage("Stage2")
            .withSlot(self.JAN_10_20)
        )
