from typing import Final

from domaindrivers.smartschedule.resource.device.device import Device
from domaindrivers.smartschedule.resource.device.device_id import DeviceId
from domaindrivers.smartschedule.resource.device.device_repository import DeviceRepository
from domaindrivers.smartschedule.resource.device.device_summary import DeviceSummary
from domaindrivers.smartschedule.shared.capability.capability import Capability


class DeviceFacade:
    __device_repository: Final[DeviceRepository]

    def __init__(self, device_repository: DeviceRepository):
        self.__device_repository = device_repository

    def find_device(self, device_id: DeviceId) -> DeviceSummary:
        return self.__device_repository.find_summary(device_id)

    def find_all_capabilities(self) -> list[Capability]:
        return self.__device_repository.find_all_capabilities()

    def create_device(self, model: str, assets: set[Capability]) -> DeviceId:
        device_id: DeviceId = DeviceId.new_one()
        device: Device = Device(device_id, model, assets)
        return self.__device_repository.save(device).id()
