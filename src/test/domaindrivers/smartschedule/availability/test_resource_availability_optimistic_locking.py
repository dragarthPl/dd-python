import concurrent.futures
from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from typing import Final
from unittest import TestCase

from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_availability import ResourceAvailability
from domaindrivers.smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from domaindrivers.smartschedule.availability.resource_availability_repository import ResourceAvailabilityRepository
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestResourceAvailabilityOptimisticLocking(TestCase):
    SQL_SCRIPTS: tuple[str] = ("schema-availability.sql",)
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)
    resource_availability_repository: ResourceAvailabilityRepository

    ONE_MONTH: Final[TimeSlot] = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.resource_availability_repository = dependency_resolver.resolve_dependency(ResourceAvailabilityRepository)

    def test_update_bumps_version(self) -> None:
        # given
        resource_availability_id: ResourceAvailabilityId = ResourceAvailabilityId.new_one()
        resource_id: ResourceAvailabilityId = ResourceAvailabilityId.new_one()
        resource_availability: ResourceAvailability = ResourceAvailability(
            resource_availability_id, resource_id, self.ONE_MONTH
        )
        self.resource_availability_repository.save_new_resource_availability(resource_availability)

        # when
        resource_availability = self.resource_availability_repository.load_by_id(resource_availability_id)
        resource_availability.block(Owner.new_one())
        self.resource_availability_repository.save_checking_version(resource_availability)

        # then
        self.assertEqual(1, self.resource_availability_repository.load_by_id(resource_availability_id).version())

    def test_cant_update_concurrently(self) -> None:
        # given
        resource_availability_id: ResourceAvailabilityId = ResourceAvailabilityId.new_one()
        resource_id: ResourceAvailabilityId = ResourceAvailabilityId.new_one()
        resource_availability: ResourceAvailability = ResourceAvailability(
            resource_availability_id, resource_id, self.ONE_MONTH
        )
        self.resource_availability_repository.save_new_resource_availability(resource_availability)
        results: list[bool] = []

        def process_resource(
            resource_availability_id: ResourceAvailabilityId,
            results: list[bool],
            resource_availability_repository: ResourceAvailabilityRepository,
        ) -> None:
            try:
                loaded: ResourceAvailability = resource_availability_repository.load_by_id(resource_availability_id)
                loaded.block(Owner.new_one())
                results.append(resource_availability_repository.save_checking_version(loaded))
            except Exception:
                # ignore exception
                pass

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for i in range(10):
                futures.append(
                    executor.submit(
                        process_resource, resource_availability_id, results, self.resource_availability_repository
                    )
                )
            concurrent.futures.wait(futures, timeout=10)

        # then
        self.assertTrue(False in results)
        self.assertTrue(self.resource_availability_repository.load_by_id(resource_availability_id).version() < 10)
