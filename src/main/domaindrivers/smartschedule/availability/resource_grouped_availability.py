from typing import Final

from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_availability import ResourceAvailability
from domaindrivers.smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.availability.segment.segment_in_minutes import SegmentInMinutes
from domaindrivers.smartschedule.availability.segment.segments import Segments
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.utils.optional import Optional


class ResourceGroupedAvailability:
    __resource_availabilities: Final[list[ResourceAvailability]]

    def __init__(self, resource_availabilities: list[ResourceAvailability]):
        self.__resource_availabilities = resource_availabilities

    @classmethod
    def of(cls, resource_id: ResourceId, time_slot: TimeSlot) -> "ResourceGroupedAvailability":
        resource_availabilities: list[ResourceAvailability] = list(
            map(
                lambda segment: ResourceAvailability(
                    availability_id=ResourceAvailabilityId.new_one(), resource_id=resource_id, segment=segment
                ),
                Segments.split(time_slot, SegmentInMinutes.default_segment()),
            )
        )
        return cls(resource_availabilities)

    @classmethod
    def of_with_parent_id(
        cls, resource_id: ResourceId, time_slot: TimeSlot, parent_id: ResourceId
    ) -> "ResourceGroupedAvailability":
        resource_availabilities: list[ResourceAvailability] = list(
            map(
                lambda segment: ResourceAvailability(
                    availability_id=ResourceAvailabilityId.new_one(),
                    resource_id=resource_id,
                    resource_parent_id=parent_id,
                    segment=segment,
                ),
                Segments.split(time_slot, SegmentInMinutes.default_segment()),
            )
        )
        return cls(resource_availabilities)

    def block(self, requester: Owner) -> bool:
        for resource_availability in self.__resource_availabilities:
            if not resource_availability.block(requester):
                return False
        return True

    def disable(self, requester: Owner) -> bool:
        for resource_availability in self.__resource_availabilities:
            if not resource_availability.disable(requester):
                return False
        return True

    def release(self, requester: Owner) -> bool:
        for resource_availability in self.__resource_availabilities:
            if not resource_availability.release(requester):
                return False
        return True

    def availabilities(self) -> list[ResourceAvailability]:
        return self.__resource_availabilities

    def resource_id(self) -> Optional[ResourceId]:
        # resourceId are the same;
        return Optional(
            next(
                map(
                    lambda resource_availability: resource_availability.resource_id(),
                    self.__resource_availabilities,
                )
            )
        )

    def size(self) -> int:
        return len(self.__resource_availabilities)

    def blocked_entirely_by(self, owner: Owner) -> bool:
        return all(map(lambda ra: ra.blocked_by() == owner, self.__resource_availabilities))

    def is_disabled_entirely_by(self, owner: Owner) -> bool:
        return all(map(lambda ra: ra.is_disabled_by(owner), self.__resource_availabilities))

    def find_blocked_by(self, owner: Owner) -> list[ResourceAvailability]:
        return list(filter(lambda ra: ra.blocked_by() == owner, self.__resource_availabilities))

    def is_entirely_available(self) -> bool:
        return any(map(lambda ra: ra.blocked_by().by_none(), self.__resource_availabilities))

    def has_no_slots(self) -> bool:
        return not self.__resource_availabilities

    def owners(self) -> set[Owner]:
        return set(map(ResourceAvailability.blocked_by, self.__resource_availabilities))
