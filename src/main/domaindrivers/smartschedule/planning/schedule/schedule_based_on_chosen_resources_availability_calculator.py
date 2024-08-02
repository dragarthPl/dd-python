from datetime import timedelta
from functools import reduce

from domaindrivers.smartschedule.availability.calendars import Calendars
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.utils.duration import ZERO


class ScheduleBasedOnChosenResourcesAvailabilityCalculator:
    def calculate(self, chosen_resources_calendars: Calendars, stages: list[Stage]) -> dict[str, TimeSlot]:
        schedule: dict[str, TimeSlot] = {}
        for stage in stages:
            proposed_slot: TimeSlot = self.__find_slot_for_stage(chosen_resources_calendars, stage)
            if proposed_slot == TimeSlot.empty():
                return {}
            schedule[stage.name] = proposed_slot
        return schedule

    def __find_slot_for_stage(self, chosen_resources_calendars: Calendars, stage: Stage) -> TimeSlot:
        found_slots: list[TimeSlot] = self.__possible_slots(chosen_resources_calendars, stage)
        if TimeSlot.empty() in found_slots:
            return TimeSlot.empty()
        common_slot_for_all_resources: TimeSlot = self.__find_common_part_of_slots(found_slots)
        while not self.__is_slot_long_enough_for_stage(stage, common_slot_for_all_resources):
            common_slot_for_all_resources = common_slot_for_all_resources.stretch(timedelta(days=1))
        return TimeSlot(common_slot_for_all_resources.since, common_slot_for_all_resources.since + stage.duration)

    def __is_slot_long_enough_for_stage(self, stage: Stage, slot: TimeSlot) -> bool:
        return bool((slot.duration() - stage.duration) >= ZERO)

    def __find_common_part_of_slots(self, found_slots: list[TimeSlot]) -> TimeSlot:
        return reduce(lambda x, y: x.common_part_with(y), found_slots) or TimeSlot.empty()

    def __possible_slots(self, chosen_resources_calendars: Calendars, stage: Stage) -> list[TimeSlot]:
        return list(
            map(
                lambda resource: next(
                    filter(
                        lambda slot: self.__is_slot_long_enough_for_stage(stage, slot),
                        sorted(chosen_resources_calendars.get(resource).available_slots(), key=lambda slot: slot.since),
                    ),
                    TimeSlot.empty(),
                ),
                stage.resources,
            )
        )
