from typing import Final

from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.capability_scheduler import CapabilityScheduler
from domaindrivers.smartschedule.resource.device.device_id import DeviceId
from domaindrivers.smartschedule.resource.device.device_repository import DeviceRepository
from domaindrivers.smartschedule.resource.device.device_summary import DeviceSummary
from domaindrivers.smartschedule.shared.capability_selector import CapabilitySelector
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class ScheduleDeviceCapabilities:
    __device_repository: Final[DeviceRepository]
    __capability_scheduler: Final[CapabilityScheduler]

    def __init__(self, device_repository: DeviceRepository, capability_scheduler: CapabilityScheduler) -> None:
        self.__device_repository = device_repository
        self.__capability_scheduler = capability_scheduler

    def setup_device_capabilities(self, device_id: DeviceId, time_slot: TimeSlot) -> list[AllocatableCapabilityId]:
        summary: DeviceSummary = self.__device_repository.find_summary(device_id)
        return self.__capability_scheduler.schedule_resource_capabilities_for_period(
            device_id.to_allocatable_resource_id(),
            [CapabilitySelector.can_perform_all_at_the_time(summary.assets)],
            time_slot,
        )
