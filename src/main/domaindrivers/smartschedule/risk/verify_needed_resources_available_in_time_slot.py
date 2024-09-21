from typing import Final

from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.availability.calendars import Calendars
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.planning.needed_resources_chosen import NeededResourcesChosen
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.risk.risk_push_notification import RiskPushNotification
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class VerifyNeededResourcesAvailableInTimeSlot:
    __availability_facade: Final[AvailabilityFacade]
    __risk_push_notification: Final[RiskPushNotification]

    def __init__(self, availability_facade: AvailabilityFacade, risk_push_notification: RiskPushNotification) -> None:
        self.__availability_facade = availability_facade
        self.__risk_push_notification = risk_push_notification

    # @EventListener
    def handle(self, resources_needed: NeededResourcesChosen) -> None:
        self.__notify_about_not_available_resources(
            resources_needed.needed_resources, resources_needed.time_slot, resources_needed.project_id
        )

    def __notify_about_not_available_resources(
        self, resourced_ids: set[ResourceId], time_slot: TimeSlot, project_id: ProjectId
    ) -> None:
        not_available: set[ResourceId] = set()
        calendars: Calendars = self.__availability_facade.load_calendars(resourced_ids, time_slot)
        for resource_id in resourced_ids:
            if not any(
                time_slot.within(available_slot) for available_slot in calendars.get(resource_id).available_slots()
            ):
                not_available.add(resource_id)
        if not_available:
            self.__risk_push_notification.notify_about_resources_not_available(project_id, not_available)
