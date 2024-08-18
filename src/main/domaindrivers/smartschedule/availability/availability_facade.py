from typing import Final

import injector
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_availability_repository import ResourceAvailabilityRepository
from domaindrivers.smartschedule.availability.resource_grouped_availability import ResourceGroupedAvailability
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.availability.segment.segment_in_minutes import SegmentInMinutes
from domaindrivers.smartschedule.availability.segment.segments import Segments
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from sqlalchemy.orm import Session


class AvailabilityFacade:
    __availability_repository: Final[ResourceAvailabilityRepository]
    __session: Session

    @injector.inject
    def __init__(self, session: Session, resource_availability_repository: ResourceAvailabilityRepository):
        self.__session = session
        self.__availability_repository = resource_availability_repository

    def create_resource_slots(self, resource_id: ResourceId, timeslot: TimeSlot) -> None:
        grouped_availability: ResourceGroupedAvailability = ResourceGroupedAvailability.of(resource_id, timeslot)
        self.__availability_repository.save_new_resource_grouped_availability(grouped_availability)

    def create_resource_slots_with_parent_id(
        self, resource_id: ResourceId, parent_id: ResourceId, time_slot: TimeSlot
    ) -> None:
        grouped_availability: ResourceGroupedAvailability = ResourceGroupedAvailability.of_with_parent_id(
            resource_id, time_slot, parent_id
        )
        self.__availability_repository.save_new_resource_grouped_availability(grouped_availability)

    def block(self, resource_id: ResourceId, time_slot: TimeSlot, requester: Owner) -> bool:
        with self.__session.begin_nested():
            to_block: ResourceGroupedAvailability = self.find_grouped(resource_id, time_slot)
            return self.__block(requester, to_block)

    def __block(self, requester: Owner, to_block: ResourceGroupedAvailability) -> bool:
        result: bool = to_block.block(requester)
        if result:
            return self.__availability_repository.save_checking_version_by_resource_grouped_availability(to_block)
        return bool(result)

    def release(self, resource_id: ResourceId, time_slot: TimeSlot, requester: Owner) -> bool:
        with self.__session.begin_nested():
            to_release: ResourceGroupedAvailability = self.find_grouped(resource_id, time_slot)
            result: bool = to_release.release(requester)
            if result:
                return self.__availability_repository.save_checking_version_by_resource_grouped_availability(to_release)
            return result

    def disable(self, resource_id: ResourceId, time_slot: TimeSlot, requester: Owner) -> bool:
        with self.__session.begin_nested():
            to_disable: ResourceGroupedAvailability = self.find_grouped(resource_id, time_slot)
            result: bool = to_disable.disable(requester)
            if result:
                result = self.__availability_repository.save_checking_version_by_resource_grouped_availability(
                    to_disable
                )
            return result

    def find_grouped(self, resource_id: ResourceId, within: TimeSlot) -> ResourceGroupedAvailability:
        normalized: TimeSlot = Segments.normalize_to_segment_boundaries(within, SegmentInMinutes.default_segment())
        return ResourceGroupedAvailability(self.__availability_repository.load_all_within_slot(resource_id, normalized))

    def find(self, resource_id: ResourceId, within: TimeSlot) -> ResourceGroupedAvailability:
        normalized: TimeSlot = Segments.normalize_to_segment_boundaries(within, SegmentInMinutes.default_segment())
        return ResourceGroupedAvailability(self.__availability_repository.load_all_within_slot(resource_id, normalized))

    def find_by_parent_id(self, parent_id: ResourceId, within: TimeSlot) -> ResourceGroupedAvailability:
        normalized: TimeSlot = Segments.normalize_to_segment_boundaries(within, SegmentInMinutes.default_segment())
        return ResourceGroupedAvailability(
            self.__availability_repository.load_all_by_parent_id_within_slot(parent_id, normalized)
        )
