import hashlib
from typing import Any, Final

from domaindrivers.smartschedule.availability.blockade import Blockade
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class ResourceAvailability:
    _id: Final[ResourceAvailabilityId]
    _resource_id: Final[ResourceId]
    _resource_parent_id: Final[ResourceId]
    _segment: Final[TimeSlot]
    _blockade: Blockade
    _version: int = 0

    def __init__(
        self,
        availability_id: ResourceAvailabilityId,
        resource_id: ResourceId,
        segment: TimeSlot,
        resource_parent_id: ResourceId = ResourceId.none(),
        blockade: Blockade = Blockade.none(),
        version: int = 0,
    ):
        self._id = availability_id
        self._resource_id = resource_id
        self._resource_parent_id = resource_parent_id
        self._segment = segment
        self._blockade = blockade
        self._version = version

    def id(self) -> ResourceAvailabilityId:
        return self._id

    def block(self, requester: Owner) -> bool:
        if self.is_available_for(requester):
            self._blockade = Blockade.owned_by(requester)
            return True
        else:
            return False

    def release(self, requester: Owner) -> bool:
        if self.is_available_for(requester):
            self._blockade = Blockade.none()
            return True
        else:
            return False

    def disable(self, requester: Owner) -> bool:
        self._blockade = Blockade.disabled_by(requester)
        return True

    def enable(self, requester: Owner) -> bool:
        if self._blockade.can_be_taken_by(requester):
            self._blockade = Blockade.none()
            return True
        return False

    def is_disabled(self) -> bool:
        return self._blockade.disabled

    def is_available_for(self, requester: Owner) -> bool:
        return self._blockade.can_be_taken_by(requester) and not self.is_disabled()

    def version(self) -> int:
        return self._version

    def blocked_by(self) -> Owner:
        return self._blockade.taken_by

    def is_disabled_by(self, owner: Owner) -> bool:
        return self._blockade.is_disabled_by(owner)

    def segment(self) -> TimeSlot:
        return self._segment

    def resource_id(self) -> ResourceId:
        return self._resource_id

    def __eq__(self, other: Any) -> bool:
        if other is None or not isinstance(other, ResourceAvailability):
            return False
        return bool(self._id == other._id)

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self._id).encode("utf-8"))

        return int(m.hexdigest(), 16)

    def resource_parent_id(self) -> ResourceId:
        return self._resource_parent_id
