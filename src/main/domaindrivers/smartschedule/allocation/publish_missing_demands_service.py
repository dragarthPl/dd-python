from datetime import datetime
from typing import Final

from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.not_satisfied_demands import NotSatisfiedDemands
from domaindrivers.smartschedule.allocation.project_allocations import ProjectAllocations
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.allocation.project_allocations_repository import ProjectAllocationsRepository
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher


class CreateHourlyDemandsSummaryService:
    def create(self, project_allocations: list[ProjectAllocations], when: datetime) -> NotSatisfiedDemands:
        missing_demands: dict[ProjectAllocationsId, Demands] = {
            _project_allocation.id: _project_allocation.missing_demands()
            for _project_allocation in filter(
                lambda project_allocation: project_allocation.has_time_slot(), project_allocations
            )
        }
        return NotSatisfiedDemands.of(missing_demands, when)


class PublishMissingDemandsService:
    __project_allocations_repository: Final[ProjectAllocationsRepository]
    __create_hourly_demands_summary_service: Final[CreateHourlyDemandsSummaryService]
    __events_publisher: Final[EventsPublisher]

    def __init__(
        self,
        project_allocations_repository: ProjectAllocationsRepository,
        create_hourly_demands_summary_service: CreateHourlyDemandsSummaryService,
        events_publisher: EventsPublisher,
    ) -> None:
        self.__project_allocations_repository = project_allocations_repository
        self.__create_hourly_demands_summary_service = create_hourly_demands_summary_service
        self.__events_publisher = events_publisher

    # @Scheduled(cron = "@hourly")
    def publish(self) -> None:
        when: datetime = datetime.now()
        project_allocations: list[ProjectAllocations] = self.__project_allocations_repository.find_all_containing_date(
            when
        )
        missing_demands: NotSatisfiedDemands = self.__create_hourly_demands_summary_service.create(
            project_allocations, when
        )
        # add metadata to event
        # if needed call EventStore and translate multiple private events to a new published event
        self.__events_publisher.publish(missing_demands)
