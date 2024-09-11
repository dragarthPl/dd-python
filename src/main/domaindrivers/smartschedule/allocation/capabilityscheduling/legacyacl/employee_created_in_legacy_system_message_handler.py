from typing import Final
from uuid import UUID

from attr import frozen
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_resource_id import AllocatableResourceId
from domaindrivers.smartschedule.allocation.capabilityscheduling.capability_scheduler import CapabilityScheduler
from domaindrivers.smartschedule.allocation.capabilityscheduling.legacyacl.translate_to_capability_selector import (
    TranslateToCapabilitySelector,
)
from domaindrivers.smartschedule.shared.capability_selector import CapabilitySelector
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


@frozen
class EmployeeDataFromLegacyEsbMessage:
    resource_id: UUID
    skills_performed_together: list[list[str]]
    exclusive_skills: list[str]
    permissions: list[str]
    time_slot: TimeSlot


class EmployeeCreatedInLegacySystemMessageHandler:
    __capability_scheduler: Final[CapabilityScheduler]

    def __init__(self, capability_scheduler: CapabilityScheduler):
        self.__capability_scheduler = capability_scheduler

    # subscribe to message bus
    # StreamListener to (message_bus)
    def handle(self, message: EmployeeDataFromLegacyEsbMessage) -> None:
        allocatable_resource_id: AllocatableResourceId = AllocatableResourceId(message.resource_id)
        capability_selectors: list[CapabilitySelector] = TranslateToCapabilitySelector().translate(message)
        self.__capability_scheduler.schedule_resource_capabilities_for_period(
            allocatable_resource_id, capability_selectors, message.time_slot
        )
