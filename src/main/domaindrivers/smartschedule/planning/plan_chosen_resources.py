from datetime import datetime
from functools import reduce
from typing import Final

import pytz
from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.availability.calendars import Calendars
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.planning.chosen_resources import ChosenResources
from domaindrivers.smartschedule.planning.needed_resources_chosen import NeededResourcesChosen
from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.planning.project import Project
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.planning.project_repository import ProjectRepository
from domaindrivers.smartschedule.planning.schedule.schedule import Schedule
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from sqlalchemy.orm import Session


class PlanChosenResources:
    __session: Session
    __project_repository: ProjectRepository
    __availability_facade: AvailabilityFacade
    __events_publisher: Final[EventsPublisher]

    def __init__(
        self,
        session: Session,
        project_repository: ProjectRepository,
        availability_facade: AvailabilityFacade,
        events_publisher: EventsPublisher,
    ):
        self.__session = session
        self.__project_repository = project_repository
        self.__availability_facade = availability_facade
        self.__events_publisher = events_publisher

    def define_resources_within_dates(
        self, project_id: ProjectId, chosen_resources: set[ResourceId], time_boundaries: TimeSlot
    ) -> None:
        with self.__session.begin_nested():
            project: Project = self.__project_repository.find_by_id(project_id).or_else_throw()
            project.add_chosen_resources(ChosenResources(chosen_resources, time_boundaries))
            self.__events_publisher.publish(
                NeededResourcesChosen(project_id, chosen_resources, time_boundaries, datetime.now(pytz.UTC))
            )

    def adjust_stages_to_resource_availability(
        self, project_id: ProjectId, time_boundaries: TimeSlot, *stages: Stage
    ) -> None:
        with self.__session.begin_nested():
            needed_resources: set[ResourceId] = self.__needed_resources(list(stages))
            project: Project = self.__project_repository.find_by_id(project_id).or_else_throw()
            self.define_resources_within_dates(project_id, needed_resources, time_boundaries)
            needed_resources_calendars: Calendars = self.__availability_facade.load_calendars(
                needed_resources, time_boundaries
            )
            schedule: Schedule = self.__create_schedule_adjusting_to_calendars(needed_resources_calendars, list(stages))
            project.add_schedule_direct(schedule)

    def __create_schedule_adjusting_to_calendars(
        self, needed_resources_calendars: Calendars, stages: list[Stage]
    ) -> Schedule:
        return Schedule.based_on_chosen_resources_availability(needed_resources_calendars, stages)

    def __needed_resources(self, stages: list[Stage]) -> set[ResourceId]:
        return reduce(lambda n, m: n.union(m), map(lambda stage: stage.resources, stages), set())
