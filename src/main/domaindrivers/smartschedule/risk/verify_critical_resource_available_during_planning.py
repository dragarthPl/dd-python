from typing import Final

from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.availability.calendar import Calendar
from domaindrivers.smartschedule.planning.critical_stage_planned import CriticalStagePlanned
from domaindrivers.smartschedule.risk.risk_push_notification import RiskPushNotification
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class VerifyCriticalResourceAvailableDuringPlanning:
    __availability_facade: Final[AvailabilityFacade]
    __risk_push_notification: Final[RiskPushNotification]

    def __init__(self, availability_facade: AvailabilityFacade, risk_push_notification: RiskPushNotification) -> None:
        self.__availability_facade = availability_facade
        self.__risk_push_notification = risk_push_notification

    # @EventListener
    def handle(self, critical_stage_planned: CriticalStagePlanned) -> None:
        if not critical_stage_planned.critical_resource:
            return
        calendar: Calendar = self.__availability_facade.load_calendar(
            critical_stage_planned.critical_resource, critical_stage_planned.stage_time_slot
        )
        if not self.__resource_is_available(critical_stage_planned.stage_time_slot, calendar):
            self.__risk_push_notification.notify_about_critical_resource_not_available(
                critical_stage_planned.project_id,
                critical_stage_planned.critical_resource,
                critical_stage_planned.stage_time_slot,
            )

    def __resource_is_available(self, time_slot: TimeSlot, calendar: Calendar) -> bool:
        return any(slot == time_slot for slot in calendar.available_slots())
