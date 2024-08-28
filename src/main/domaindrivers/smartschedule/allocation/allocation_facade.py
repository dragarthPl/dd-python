from datetime import datetime
from typing import Final
from uuid import UUID

import pytz
from domaindrivers.smartschedule.allocation.allocations import Allocations
from domaindrivers.smartschedule.allocation.capabilities_allocated import CapabilitiesAllocated
from domaindrivers.smartschedule.allocation.capability_released import CapabilityReleased
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocations import ProjectAllocations
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.allocation.project_allocations_repository import ProjectAllocationsRepository
from domaindrivers.smartschedule.allocation.projects_allocations_summary import ProjectsAllocationsSummary
from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.utils.optional import Optional
from sqlalchemy.orm import Session


class AllocationFacade:
    __session: Session
    __project_allocations_repository: Final[ProjectAllocationsRepository]
    __availability_facade: Final[AvailabilityFacade]

    def __init__(
        self,
        session: Session,
        project_allocations_repository: ProjectAllocationsRepository,
        availability_facade: AvailabilityFacade,
    ):
        self.__session: Session = session
        self.__project_allocations_repository = project_allocations_repository
        self.__availability_facade = availability_facade

    # @Transactional
    def create_allocation(self, time_slot: TimeSlot, scheduled_demands: Demands) -> ProjectAllocationsId:
        with self.__session.begin_nested():
            project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
            project_allocations: ProjectAllocations = ProjectAllocations(
                project_id, Allocations.none(), scheduled_demands, time_slot
            )
            self.__project_allocations_repository.save(project_allocations)
            return project_id

    def find_all_projects_allocations_by(self, project_ids: set[ProjectAllocationsId]) -> ProjectsAllocationsSummary:
        return ProjectsAllocationsSummary.of(self.__project_allocations_repository.find_all_by_id(project_ids))

    def find_all_projects_allocations(self) -> ProjectsAllocationsSummary:
        return ProjectsAllocationsSummary.of(self.__project_allocations_repository.find_all())

    # @Transactional
    def allocate_to_project(
        self, project_id: ProjectAllocationsId, resource_id: ResourceId, capability: Capability, time_slot: TimeSlot
    ) -> Optional[UUID]:
        with self.__session.begin_nested():
            # TODO WHAT TO DO WITH AVAILABILITY HERE? - implement
            allocations: ProjectAllocations = self.__project_allocations_repository.find_by_id(
                project_id
            ).or_else_throw()
            event: Optional[CapabilitiesAllocated] = allocations.allocate(
                resource_id, capability, time_slot, datetime.now(pytz.UTC)
            )
            self.__project_allocations_repository.save(allocations)
            return event.map(lambda capabilities_allocated: capabilities_allocated.allocated_capability_id)

    # @Transactional
    def release_from_project(
        self, project_id: ProjectAllocationsId, allocatable_capability_id: UUID, time_slot: TimeSlot
    ) -> bool:
        with self.__session.begin_nested():
            # TODO WHAT TO DO WITH AVAILABILITY HERE? - just think about it, don't implement
            allocations: ProjectAllocations = self.__project_allocations_repository.find_by_id(
                project_id
            ).or_else_throw()
            event: Optional[CapabilityReleased] = allocations.release(
                allocatable_capability_id, time_slot, datetime.now(pytz.UTC)
            )
            self.__project_allocations_repository.save(allocations)
            return event.is_present()

    # @Transactional
    def edit_project_dates(self, project_id: ProjectAllocationsId, from_to: TimeSlot) -> None:
        with self.__session.begin_nested():
            project_allocations: ProjectAllocations = self.__project_allocations_repository.find_by_id(
                project_id
            ).or_else_throw()
            project_allocations.define_slot(from_to, datetime.now(pytz.UTC))

    # @Transactional
    def schedule_project_allocation_demands(self, project_id: ProjectAllocationsId, demands: Demands) -> None:
        with self.__session.begin_nested():
            project_allocations: ProjectAllocations = self.__project_allocations_repository.find_by_id(
                project_id
            ).or_else_get(lambda: ProjectAllocations.empty(project_id))
            project_allocations.add_demands(demands, datetime.now(pytz.UTC))
            self.__project_allocations_repository.save(project_allocations)
