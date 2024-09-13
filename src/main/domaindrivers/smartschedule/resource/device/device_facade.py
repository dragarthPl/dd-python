from typing import Final

from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.resource.device.device import Device
from domaindrivers.smartschedule.resource.device.device_id import DeviceId
from domaindrivers.smartschedule.resource.device.device_repository import DeviceRepository
from domaindrivers.smartschedule.resource.device.device_summary import DeviceSummary
from domaindrivers.smartschedule.resource.device.schedule_device_capabilities import ScheduleDeviceCapabilities
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class DeviceFacade:
    __device_repository: Final[DeviceRepository]
    __schedule_device_capabilities: Final[ScheduleDeviceCapabilities]

    def __init__(self, device_repository: DeviceRepository, schedule_device_capabilities: ScheduleDeviceCapabilities):
        self.__device_repository = device_repository
        self.__schedule_device_capabilities = schedule_device_capabilities

    def find_device(self, device_id: DeviceId) -> DeviceSummary:
        return self.__device_repository.find_summary(device_id)

    def find_all_capabilities(self) -> list[Capability]:
        return self.__device_repository.find_all_capabilities()

    def create_device(self, model: str, assets: set[Capability]) -> DeviceId:
        device_id: DeviceId = DeviceId.new_one()
        device: Device = Device(device_id, model, assets)
        return self.__device_repository.save(device).id()

    def schedule_capabilities(self, device_id: DeviceId, one_day: TimeSlot) -> list[AllocatableCapabilityId]:
        return self.__schedule_device_capabilities.setup_device_capabilities(device_id, one_day)
