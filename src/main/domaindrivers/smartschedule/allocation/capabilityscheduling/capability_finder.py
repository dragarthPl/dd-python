from typing import Final

from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capabilities_summary import (
    AllocatableCapabilitiesSummary,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability import AllocatableCapability
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_repository import (
    AllocatableCapabilityRepository,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_summary import (
    AllocatableCapabilitySummary,
)
from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.availability.calendars import Calendars
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class CapabilityFinder:
    __availability_facade: Final[AvailabilityFacade]
    __allocatable_resource_repository: Final[AllocatableCapabilityRepository]

    def __init__(
        self, availability_facade: AvailabilityFacade, allocatable_resource_repository: AllocatableCapabilityRepository
    ) -> None:
        self.__availability_facade = availability_facade
        self.__allocatable_resource_repository = allocatable_resource_repository

    def find_available_capabilities(
        self, capability: Capability, time_slot: TimeSlot
    ) -> AllocatableCapabilitiesSummary:
        find_allocatable_capability: list[AllocatableCapability] = (
            self.__allocatable_resource_repository.find_by_capability_within(
                capability.name, capability.type, time_slot.since, time_slot.to
            )
        )
        found: list[AllocatableCapability] = self.__filter_availability_in_time_slot(
            find_allocatable_capability, time_slot
        )
        return self.__create_summary(found)

    def find_capabilities(self, capability: Capability, time_slot: TimeSlot) -> AllocatableCapabilitiesSummary:
        found: list[AllocatableCapability] = self.__allocatable_resource_repository.find_by_capability_within(
            capability.name, capability.type, time_slot.since, time_slot.to
        )
        return self.__create_summary(found)

    def find_by_ids(self, allocatable_capability_ids: list[AllocatableCapabilityId]) -> AllocatableCapabilitiesSummary:
        all_by_id_in: list[AllocatableCapability] = self.__allocatable_resource_repository.find_all_by_id(
            set(allocatable_capability_ids)
        )
        return self.__create_summary(all_by_id_in)

    def find_by_id(self, allocatable_capability_id: AllocatableCapabilityId) -> AllocatableCapabilitySummary:
        return (
            self.__allocatable_resource_repository.find_by_id(allocatable_capability_id)
            .map(
                self.__create_single_summary,
            )
            .or_else(None)
        )

    def __filter_availability_in_time_slot(
        self, find_allocatable_capability: list[AllocatableCapability], time_slot: TimeSlot
    ) -> list[AllocatableCapability]:
        resource_ids: set[ResourceId] = set(
            map(lambda ac: ac.id().to_availability_resource_id(), find_allocatable_capability)
        )
        calendars: Calendars = self.__availability_facade.load_calendars(resource_ids, time_slot)
        return list(
            filter(
                lambda ac: time_slot in calendars.get(ac.id().to_availability_resource_id()).available_slots(),
                find_allocatable_capability,
            )
        )

    def __create_summary(self, since: list[AllocatableCapability]) -> AllocatableCapabilitiesSummary:
        return AllocatableCapabilitiesSummary(
            list(
                map(
                    self.__create_single_summary,
                    since,
                )
            )
        )

    def __create_single_summary(self, allocatable_capability: AllocatableCapability) -> AllocatableCapabilitySummary:
        return AllocatableCapabilitySummary(
            allocatable_capability.id(),
            allocatable_capability.resource_id(),
            allocatable_capability.capabilities(),
            allocatable_capability.slot(),
        )
