from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from typing import Final
from unittest import TestCase

from domaindrivers.smartschedule.availability.resource_availability import ResourceAvailability
from domaindrivers.smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from domaindrivers.smartschedule.availability.resource_availability_repository import ResourceAvailabilityRepository
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestResourceAvailabilityLoading(TestCase):
    SQL_SCRIPTS: tuple[str] = ("schema-availability.sql",)
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)
    resource_availability_repository: ResourceAvailabilityRepository

    ONE_MONTH: Final[TimeSlot] = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.resource_availability_repository = dependency_resolver.resolve_dependency(ResourceAvailabilityRepository)

    def test_can_save_and_load_by_id(self) -> None:
        # given
        resource_availability_id: ResourceAvailabilityId = ResourceAvailabilityId.new_one()
        resource_id: ResourceId = ResourceId.new_one()
        resource_availability: ResourceAvailability = ResourceAvailability(
            resource_availability_id, resource_id, self.ONE_MONTH
        )

        # when
        self.resource_availability_repository.save_new_resource_availability(resource_availability)

        # then
        loaded: ResourceAvailability = self.resource_availability_repository.load_by_id(resource_availability.id())
        self.assertEqual(resource_availability, loaded)
        self.assertEqual(resource_availability.segment(), loaded.segment())
        self.assertEqual(resource_availability.resource_id(), loaded.resource_id())
        self.assertEqual(resource_availability.blocked_by(), loaded.blocked_by())
