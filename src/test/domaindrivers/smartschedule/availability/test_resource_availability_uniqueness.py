from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from typing import Final
from unittest import TestCase

from domaindrivers.smartschedule.availability.resource_availability import ResourceAvailability
from domaindrivers.smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from domaindrivers.smartschedule.availability.resource_availability_repository import ResourceAvailabilityRepository
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from sqlalchemy.exc import IntegrityError


class TestResourceAvailabilityUniqueness(TestCase):
    SQL_SCRIPTS: tuple[str] = ("schema-availability.sql",)
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)
    resource_availability_repository: ResourceAvailabilityRepository

    ONE_MONTH: Final[TimeSlot] = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.resource_availability_repository = dependency_resolver.resolve_dependency(ResourceAvailabilityRepository)

    def test_cant_save_two_availabilities_with_same_resource_id_and_segment(self) -> None:
        # given
        resource_id: ResourceId = ResourceId.new_one()
        another_resource_id: ResourceId = ResourceId.new_one()
        resource_availability_id: ResourceAvailabilityId = ResourceAvailabilityId.new_one()

        # when
        self.resource_availability_repository.save_new_resource_availability(
            ResourceAvailability(resource_availability_id, resource_id, self.ONE_MONTH)
        )

        # expect
        with self.assertRaises(IntegrityError):
            self.resource_availability_repository.save_new_resource_availability(
                ResourceAvailability(resource_availability_id, another_resource_id, self.ONE_MONTH)
            )
