from datetime import datetime
from typing import Final

import injector
import pytz
from domaindrivers.smartschedule.availability.calendar import Calendar
from domaindrivers.smartschedule.availability.calendars import Calendars
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_availability_read_model import ResourceAvailabilityReadModel
from domaindrivers.smartschedule.availability.resource_availability_repository import ResourceAvailabilityRepository
from domaindrivers.smartschedule.availability.resource_grouped_availability import ResourceGroupedAvailability
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.availability.resource_taken_over import ResourceTakenOver
from domaindrivers.smartschedule.availability.segment.segment_in_minutes import SegmentInMinutes
from domaindrivers.smartschedule.availability.segment.segments import Segments
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.utils.optional import Optional
from sqlalchemy.orm import Session


class AvailabilityFacade:
    __session: Session
    __availability_repository: Final[ResourceAvailabilityRepository]
    __availability_read_model: Final[ResourceAvailabilityReadModel]
    __events_publisher: Final[EventsPublisher]

    @injector.inject
    def __init__(
        self,
        session: Session,
        resource_availability_repository: ResourceAvailabilityRepository,
        resource_availability_read_model: ResourceAvailabilityReadModel,
        events_publisher: EventsPublisher,
    ):
        self.__session = session
        self.__availability_repository = resource_availability_repository
        self.__availability_read_model = resource_availability_read_model
        self.__events_publisher = events_publisher

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
        if to_block.has_no_slots():
            return False
        result: bool = to_block.block(requester)
        if result:
            return self.__availability_repository.save_checking_version_by_resource_grouped_availability(to_block)
        return bool(result)

    def release(self, resource_id: ResourceId, time_slot: TimeSlot, requester: Owner) -> bool:
        with self.__session.begin_nested():
            to_release: ResourceGroupedAvailability = self.find_grouped(resource_id, time_slot)
            if to_release.has_no_slots():
                return False
            result: bool = to_release.release(requester)
            if result:
                return self.__availability_repository.save_checking_version_by_resource_grouped_availability(to_release)
            return result

    def disable(self, resource_id: ResourceId, time_slot: TimeSlot, requester: Owner) -> bool:
        with self.__session.begin_nested():
            to_disable: ResourceGroupedAvailability = self.find_grouped(resource_id, time_slot)
            if to_disable.has_no_slots():
                return False
            previous_owners: set[Owner] = to_disable.owners()
            result: bool = to_disable.disable(requester)
            if result:
                result = self.__availability_repository.save_checking_version_by_resource_grouped_availability(
                    to_disable
                )
                if result:
                    self.__events_publisher.publish(
                        ResourceTakenOver.of(resource_id, previous_owners, time_slot, datetime.now(pytz.UTC))
                    )
            return result

    def block_random_available(
        self, resource_ids: set[ResourceId], within: TimeSlot, owner: Owner
    ) -> Optional[ResourceId]:
        with self.__session.begin_nested():
            normalized: TimeSlot = Segments.normalize_to_segment_boundaries(within, SegmentInMinutes.default_segment())
            grouped_availability: ResourceGroupedAvailability = (
                self.__availability_repository.load_availabilities_of_random_resource_within(resource_ids, normalized)
            )
            if self.__block(owner, grouped_availability):
                return grouped_availability.resource_id()
            else:
                return Optional.empty()

    def find_grouped(self, resource_id: ResourceId, within: TimeSlot) -> ResourceGroupedAvailability:
        normalized: TimeSlot = Segments.normalize_to_segment_boundaries(within, SegmentInMinutes.default_segment())
        return ResourceGroupedAvailability(self.__availability_repository.load_all_within_slot(resource_id, normalized))

    def load_calendar(self, resource_id: ResourceId, within: TimeSlot) -> Calendar:
        normalized: TimeSlot = Segments.normalize_to_segment_boundaries(within, SegmentInMinutes.default_segment())
        return self.__availability_read_model.load(resource_id, normalized)

    def load_calendars(self, resources: set[ResourceId], within: TimeSlot) -> Calendars:
        normalized: TimeSlot = Segments.normalize_to_segment_boundaries(within, SegmentInMinutes.default_segment())
        return self.__availability_read_model.load_all(resources, normalized)

    def find(self, resource_id: ResourceId, within: TimeSlot) -> ResourceGroupedAvailability:
        normalized: TimeSlot = Segments.normalize_to_segment_boundaries(within, SegmentInMinutes.default_segment())
        return ResourceGroupedAvailability(self.__availability_repository.load_all_within_slot(resource_id, normalized))

    def find_by_parent_id(self, parent_id: ResourceId, within: TimeSlot) -> ResourceGroupedAvailability:
        normalized: TimeSlot = Segments.normalize_to_segment_boundaries(within, SegmentInMinutes.default_segment())
        return ResourceGroupedAvailability(
            self.__availability_repository.load_all_by_parent_id_within_slot(parent_id, normalized)
        )
