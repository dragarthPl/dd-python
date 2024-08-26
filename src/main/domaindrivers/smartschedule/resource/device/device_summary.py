from attr import frozen
from domaindrivers.smartschedule.resource.device.device_id import DeviceId
from domaindrivers.smartschedule.shared.capability.capability import Capability


@frozen
class DeviceSummary:
    __device_id: DeviceId
    model: str
    assets: set[Capability]
