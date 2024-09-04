from typing import Final

from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability import AllocatableCapability
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_repository import (
    AllocatableCapabilityRepository,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_resource_id import AllocatableResourceId
from domaindrivers.smartschedule.allocation.capabilityscheduling.capability_selector import CapabilitySelector
from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from sqlalchemy.orm import Session


class CapabilityScheduler:
    __session: Final[Session]
    __availability_facade: Final[AvailabilityFacade]
    __allocatable_resource_repository: Final[AllocatableCapabilityRepository]

    def __init__(
        self,
        session: Session,
        availability_facade: AvailabilityFacade,
        allocatable_resource_repository: AllocatableCapabilityRepository,
    ) -> None:
        self.__session = session
        self.__availability_facade = availability_facade
        self.__allocatable_resource_repository = allocatable_resource_repository

    def schedule_resource_capabilities_for_period(
        self, resource_id: AllocatableResourceId, capabilities: list[CapabilitySelector], time_slot: TimeSlot
    ) -> list[AllocatableCapabilityId]:
        with self.__session.begin_nested():
            allocatable_resource_ids: list[AllocatableCapabilityId] = self.__create_allocatable_resources(
                resource_id, capabilities, time_slot
            )
            for resource in allocatable_resource_ids:
                self.__availability_facade.create_resource_slots(resource.to_availability_resource_id(), time_slot)
            return allocatable_resource_ids

    def schedule_multiple_resources_for_period(
        self, resources: set[AllocatableResourceId], capability: Capability, time_slot: TimeSlot
    ) -> list[AllocatableCapabilityId]:
        with self.__session.begin_nested():
            allocatable_capability: list[AllocatableCapability] = list(
                map(
                    lambda resource: AllocatableCapability(
                        allocatable_resource_id=resource,
                        possible_capabilities=CapabilitySelector.can_just_perform(capability),
                        time_slot=time_slot,
                    ),
                    resources,
                )
            )
            self.__allocatable_resource_repository.save_all(allocatable_capability)
            for resource in allocatable_capability:
                self.__availability_facade.create_resource_slots(resource.id().to_availability_resource_id(), time_slot)
            return list(map(lambda allocatable_capability: allocatable_capability.id(), allocatable_capability))

    def __create_allocatable_resources(
        self, resource_id: AllocatableResourceId, capabilities: list[CapabilitySelector], time_slot: TimeSlot
    ) -> list[AllocatableCapabilityId]:
        allocatable_resources: list[AllocatableCapability] = list(
            map(
                lambda capability: AllocatableCapability(
                    allocatable_resource_id=resource_id, possible_capabilities=capability, time_slot=time_slot
                ),
                capabilities,
            )
        )
        self.__allocatable_resource_repository.save_all(allocatable_resources)
        return list(map(lambda allocatable_capability: allocatable_capability.id(), allocatable_resources))

    def find_resource_capabilities(
        self, resource_id: AllocatableResourceId, capability: Capability, period: TimeSlot
    ) -> AllocatableCapabilityId:
        return (
            self.__allocatable_resource_repository.find_by_resource_id_and_capability_and_time_slot(
                resource_id.id(), capability.name, capability.type, period.since, period.to
            )
            .map(lambda allocatable_capability: allocatable_capability.id())
            .or_else(None)
        )

    def find_resource_by_resource_id_and_time_slot_capabilities(
        self, allocatable_resource_id: AllocatableResourceId, capabilities: set[Capability], time_slot: TimeSlot
    ) -> AllocatableCapabilityId:
        return next(
            map(
                lambda allocatable_capability: allocatable_capability.id(),
                filter(
                    lambda ac: ac.can_perform(capabilities),
                    self.__allocatable_resource_repository.find_by_resource_id_and_time_slot(
                        allocatable_resource_id.id(), time_slot.since, time_slot.to
                    ),
                ),
            ),
            None,
        )
