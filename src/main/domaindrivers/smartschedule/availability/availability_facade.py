from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class AvailabilityFacade:
    # can start with an in-memory repository for the aggregate

    def create_resource_slots(self, resource_id: ResourceAvailabilityId, timeslot: TimeSlot) -> None:
        pass

    def block(self, resource_id: ResourceAvailabilityId, time_slot: TimeSlot, requester: Owner) -> bool:
        return True

    def release(self, resource_id: ResourceAvailabilityId, time_slot: TimeSlot, requester: Owner) -> bool:
        return True

    def disable(self, resource_id: ResourceAvailabilityId, time_slot: TimeSlot, requester: Owner) -> bool:
        return True
