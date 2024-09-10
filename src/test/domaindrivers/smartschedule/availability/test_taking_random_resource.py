from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from unittest import TestCase

from domaindrivers.smartschedule.availability.availability_facade import AvailabilityFacade
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_grouped_availability import ResourceGroupedAvailability
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.utils.optional import Optional


class TakingRandomResourceTest(TestCase):
    SQL_SCRIPTS: tuple[str, ...] = ("schema-availability.sql",)
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)

    availability_facade: AvailabilityFacade

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.availability_facade = dependency_resolver.resolve_dependency(AvailabilityFacade)

    def test_can_take_random_resource_from_pool(self) -> None:
        # given
        resource_id: ResourceId = ResourceId.new_one()
        resource_id_2: ResourceId = ResourceId.new_one()
        resource_id_3: ResourceId = ResourceId.new_one()
        resources_pool: set[ResourceId] = {resource_id, resource_id_2, resource_id_3}
        # and
        owner_1: Owner = Owner.new_one()
        owner_2: Owner = Owner.new_one()
        owner_3: Owner = Owner.new_one()
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)

        # and
        self.availability_facade.create_resource_slots(resource_id, one_day)
        self.availability_facade.create_resource_slots(resource_id_2, one_day)
        self.availability_facade.create_resource_slots(resource_id_3, one_day)

        # when
        taken_1: Optional[ResourceId] = self.availability_facade.block_random_available(
            resources_pool, one_day, owner_1
        )

        # then
        self.assertTrue(taken_1.is_present())
        self.assertTrue(taken_1.get() in resources_pool)
        taken_1.if_present(lambda value: self.assert_that_resource_is_take_by_owner(value, owner_1, one_day))

        # when
        taken_2 = self.availability_facade.block_random_available(resources_pool, one_day, owner_2)

        # then
        self.assertTrue(taken_2.is_present())
        self.assertTrue(taken_2.get() in resources_pool)
        taken_2.if_present(lambda value: self.assert_that_resource_is_take_by_owner(value, owner_2, one_day))

        # when
        taken_3: Optional[ResourceId] = self.availability_facade.block_random_available(
            resources_pool, one_day, owner_3
        )

        # then
        self.assertTrue(taken_3.is_present())
        self.assertTrue(taken_3.get() in resources_pool)
        taken_3.if_present(lambda value: self.assert_that_resource_is_take_by_owner(value, owner_3, one_day))

        # when
        taken_4: Optional[ResourceId] = self.availability_facade.block_random_available(
            resources_pool, one_day, owner_3
        )

        # then
        self.assertFalse(taken_4.is_present())

    def test_nothing_is_taken_when_no_resource_in_pool(self) -> None:
        # given
        resources: set[ResourceId] = {ResourceId.new_one(), ResourceId.new_one(), ResourceId.new_one()}

        # when
        jan_1: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        taken_1: Optional[ResourceId] = self.availability_facade.block_random_available(
            resources, jan_1, Owner.new_one()
        )

        # then
        self.assertFalse(taken_1.is_present())

    def assert_that_resource_is_take_by_owner(self, resource_id: ResourceId, owner: Owner, one_day: TimeSlot) -> None:
        resource_availability: ResourceGroupedAvailability = self.availability_facade.find(resource_id, one_day)
        self.assertTrue(all(ra.blocked_by() == owner for ra in resource_availability.availabilities()))
