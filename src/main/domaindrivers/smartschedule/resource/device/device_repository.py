from functools import reduce

from domaindrivers.smartschedule.resource.device.device import Device
from domaindrivers.smartschedule.resource.device.device_id import DeviceId
from domaindrivers.smartschedule.resource.device.device_summary import DeviceSummary
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.storage.repository import Repository


class DeviceRepository(Repository[Device, DeviceId]):
    def find_summary(self, device_id: DeviceId) -> DeviceSummary:
        device: Device = self.find_by_id(device_id).or_else_throw()
        assets: set[Capability] = device.capabilities()
        return DeviceSummary(device_id, device.model(), assets)

    def find_all_capabilities(self) -> list[Capability]:
        return reduce(lambda n, m: n + list(m.capabilities()), self.find_all(), [])
