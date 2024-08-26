from attr import define, field
from domaindrivers.smartschedule.resource.device.device_id import DeviceId
from domaindrivers.smartschedule.shared.capability.capability import Capability


@define(slots=False)
class Device:
    _model: str

    # @Type(JsonType.class)
    # @Column(columnDefinition = "jsonb")
    _capabilities: set[Capability]
    _id: DeviceId = field(factory=DeviceId.new_one)
    _version: int = 0

    def model(self) -> str:
        return self._model

    def capabilities(self) -> set[Capability]:
        return self._capabilities

    def id(self) -> DeviceId:
        return self._id

    def __init__(
        self,
        device_id: DeviceId = DeviceId.new_one(),
        model: str = None,
        capabilities: set[Capability] = None,
    ) -> None:
        self._id = device_id
        self._model = model
        self._capabilities = capabilities
