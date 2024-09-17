import injector
from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.availability.resource_availability_read_model import ResourceAvailabilityReadModel
from domaindrivers.smartschedule.availability.resource_availability_repository import ResourceAvailabilityRepository
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher
from injector import Module, provider, singleton
from sqlalchemy.orm import Session


class AvailabilityConfiguration(Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(ResourceAvailabilityRepository, to=ResourceAvailabilityRepository)

    @singleton
    @provider
    def availability_facade(
        self,
        session: Session,
        resource_availability_repository: ResourceAvailabilityRepository,
        events_publisher: EventsPublisher,
    ) -> AvailabilityFacade:
        return AvailabilityFacade(
            session, resource_availability_repository, ResourceAvailabilityReadModel(session), events_publisher
        )
