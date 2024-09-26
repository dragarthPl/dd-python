from datetime import datetime
from typing import Final
from uuid import UUID

import pytz
from domaindrivers.smartschedule.allocation.allocations import Allocations
from domaindrivers.smartschedule.allocation.capabilities_allocated import CapabilitiesAllocated
from domaindrivers.smartschedule.allocation.capability_released import CapabilityReleased
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capabilities_summary import (
    AllocatableCapabilitiesSummary,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_summary import (
    AllocatableCapabilitySummary,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.capability_finder import CapabilityFinder
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocation_scheduled import ProjectAllocationScheduled
from domaindrivers.smartschedule.allocation.project_allocations import ProjectAllocations
from domaindrivers.smartschedule.allocation.project_allocations_demands_scheduled import (
    ProjectAllocationsDemandsScheduled,
)
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.allocation.project_allocations_repository import ProjectAllocationsRepository
from domaindrivers.smartschedule.allocation.projects_allocations_summary import ProjectsAllocationsSummary
from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.capability_selector import CapabilitySelector
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.utils.optional import Optional
from sqlalchemy.orm import Session


class AllocationFacade:
    __session: Session
    __project_allocations_repository: Final[ProjectAllocationsRepository]
    __availability_facade: Final[AvailabilityFacade]
    __capability_finder: Final[CapabilityFinder]
    __events_publisher: Final[EventsPublisher]

    def __init__(
        self,
        session: Session,
        project_allocations_repository: ProjectAllocationsRepository,
        availability_facade: AvailabilityFacade,
        capability_finder: CapabilityFinder,
        events_publisher: EventsPublisher,
    ):
        self.__session: Session = session
        self.__project_allocations_repository = project_allocations_repository
        self.__availability_facade = availability_facade
        self.__capability_finder = capability_finder
        self.__events_publisher = events_publisher

    def create_allocation(self, time_slot: TimeSlot, scheduled_demands: Demands) -> ProjectAllocationsId:
        with self.__session.begin_nested():
            project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
            project_allocations: ProjectAllocations = ProjectAllocations(
                project_id, Allocations.none(), scheduled_demands, time_slot
            )
            self.__project_allocations_repository.save(project_allocations)
            self.__events_publisher.publish(
                ProjectAllocationScheduled.of(project_id, time_slot, datetime.now(pytz.UTC))
            )
            return project_id

    def find_all_projects_allocations_by(self, project_ids: set[ProjectAllocationsId]) -> ProjectsAllocationsSummary:
        return ProjectsAllocationsSummary.of(self.__project_allocations_repository.find_all_by_id(project_ids))

    def find_all_projects_allocations(self) -> ProjectsAllocationsSummary:
        return ProjectsAllocationsSummary.of(self.__project_allocations_repository.find_all())

    def allocate_to_project(
        self,
        project_id: ProjectAllocationsId,
        allocatable_capability_id: AllocatableCapabilityId,
        time_slot: TimeSlot,
    ) -> Optional[UUID]:
        with self.__session.begin_nested():
            # yes, one transaction crossing 2 modules.
            capability: AllocatableCapabilitySummary = self.__capability_finder.find_by_id(allocatable_capability_id)
            if not capability:
                return Optional.empty()
            if not self.__availability_facade.block(
                allocatable_capability_id.to_availability_resource_id(), time_slot, Owner.of(project_id.id())
            ):
                return Optional.empty()
            event: Optional[CapabilitiesAllocated] = self.__allocate(
                project_id,
                allocatable_capability_id,
                capability.capabilities,
                time_slot,
            )
            return event.map(lambda capabilities_allocated: capabilities_allocated.allocated_capability_id)

    def __allocate(
        self,
        project_id: ProjectAllocationsId,
        allocatable_capability_id: AllocatableCapabilityId,
        capability: CapabilitySelector,
        time_slot: TimeSlot,
    ) -> Optional[CapabilitiesAllocated]:
        allocations: ProjectAllocations = self.__project_allocations_repository.find_by_id(project_id).or_else_throw()
        event: Optional[CapabilitiesAllocated] = allocations.allocate(
            allocatable_capability_id, capability, time_slot, datetime.now(pytz.UTC)
        )
        self.__project_allocations_repository.save(allocations)
        return event

    def release_from_project(
        self, project_id: ProjectAllocationsId, allocatable_capability_id: AllocatableCapabilityId, time_slot: TimeSlot
    ) -> bool:
        with self.__session.begin_nested():
            # can release not scheduled capability - at least for now. Hence no check to capabilityFinder
            self.__availability_facade.release(
                allocatable_capability_id.to_availability_resource_id(), time_slot, Owner.of(project_id.id())
            )

            allocations: ProjectAllocations = self.__project_allocations_repository.find_by_id(
                project_id
            ).or_else_throw()
            event: Optional[CapabilityReleased] = allocations.release(
                allocatable_capability_id, time_slot, datetime.now(pytz.UTC)
            )
            self.__project_allocations_repository.save(allocations)
            return event.is_present()

    def allocate_capability_to_project_for_period(
        self, project_id: ProjectAllocationsId, capability: Capability, time_slot: TimeSlot
    ) -> bool:
        with self.__session.begin_nested():
            proposed_capabilities: AllocatableCapabilitiesSummary = self.__capability_finder.find_capabilities(
                capability, time_slot
            )
            if not proposed_capabilities.all:
                return False
            availability_resource_ids: set[ResourceId] = set(
                map(
                    lambda resource: resource.allocatable_capability_id.to_availability_resource_id(),
                    proposed_capabilities.all,
                )
            )
            chosen = self.__availability_facade.block_random_available(
                availability_resource_ids, time_slot, Owner.of(project_id.id())
            )
            if chosen.is_empty():
                return False
            to_allocate: AllocatableCapabilitySummary = self.__find_chosen_allocatable_capability(
                proposed_capabilities, chosen.get()
            )
            return self.__allocate(
                project_id, to_allocate.allocatable_capability_id, to_allocate.capabilities, time_slot
            ).is_present()

    def __find_chosen_allocatable_capability(
        self, proposed_capabilities: AllocatableCapabilitiesSummary, chosen: ResourceId
    ) -> AllocatableCapabilitySummary:
        return next(
            filter(
                lambda summary: summary.allocatable_capability_id.to_availability_resource_id() == chosen,
                proposed_capabilities.all,
            ),
            None,
        )

    def edit_project_dates(self, project_id: ProjectAllocationsId, from_to: TimeSlot) -> None:
        with self.__session.begin_nested():
            project_allocations: ProjectAllocations = self.__project_allocations_repository.find_by_id(
                project_id
            ).or_else_throw()
            project_dates_set: Optional[ProjectAllocationScheduled] = project_allocations.define_slot(
                from_to, datetime.now(pytz.UTC)
            )
            project_dates_set.if_present(self.__events_publisher.publish)

    def schedule_project_allocation_demands(self, project_id: ProjectAllocationsId, demands: Demands) -> None:
        with self.__session.begin_nested():
            project_allocations: ProjectAllocations = self.__project_allocations_repository.find_by_id(
                project_id
            ).or_else_get(lambda: ProjectAllocations.empty(project_id))
            event: Optional[ProjectAllocationsDemandsScheduled] = project_allocations.add_demands(  # noqa: F841
                demands,
                datetime.now(pytz.UTC),
            )
            # event could be stored in a local store
            # always remember about transactional boundaries
            self.__project_allocations_repository.save(project_allocations)
