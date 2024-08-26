from attr import define, field
from domaindrivers.smartschedule.resource.device.device_id import DeviceId
from domaindrivers.smartschedule.shared.capability.capability import Capability


@define(slots=False)
class Device:
    _id: DeviceId = field(factory=DeviceId.new_one)
    _model: str = field(default=None)
    _capabilities: set[Capability] = field(factory=set)
    _version: int = field(default=0)

    def model(self) -> str:
        return self._model

    def capabilities(self) -> set[Capability]:
        return self._capabilities

    def id(self) -> DeviceId:
        return self._id
