from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import Callable, Generator

from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.utils.functional import BiFunction


class SlotToSegments(BiFunction[TimeSlot, "SegmentInMinutes", list[TimeSlot]]):  # type: ignore
    def apply(self, time_slot: TimeSlot, duration: "SegmentInMinutes") -> list[TimeSlot]:  # type: ignore # noqa: F821
        minimal_segment: TimeSlot = TimeSlot(time_slot.since, time_slot.since + timedelta(minutes=duration.value))
        if time_slot.within(minimal_segment):
            return [minimal_segment]
        segment_in_minutes_duration: int = duration.value
        number_of_segments: int = self.__calculate_number_of_segments(time_slot, segment_in_minutes_duration)

        def interate(start: datetime, func: Callable[[datetime], datetime], limit: int) -> Generator[datetime]:
            n = start
            for _ in range(limit):
                yield n
                n = func(n)

        return list(
            map(
                lambda current_start: TimeSlot(
                    current_start, self.__calculate_end(segment_in_minutes_duration, current_start, time_slot.to)
                ),
                interate(
                    time_slot.since,
                    lambda current_start: current_start + timedelta(minutes=segment_in_minutes_duration),
                    number_of_segments,
                ),
            )
        )

    def __calculate_number_of_segments(self, time_slot: TimeSlot, segment_in_minutes_duration: int) -> int:
        return int(math.ceil(((time_slot.to - time_slot.since).total_seconds() / 60) / segment_in_minutes_duration))

    def __calculate_end(
        self, segment_in_minutes_duration: int, current_start: datetime, initial_end: datetime
    ) -> datetime:
        segment_end: datetime = current_start + timedelta(minutes=segment_in_minutes_duration)
        if initial_end < segment_end:
            return initial_end
        return segment_end
