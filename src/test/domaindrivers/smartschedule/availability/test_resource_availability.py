from unittest import TestCase

from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_availability import ResourceAvailability
from domaindrivers.smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestResourceAvailability(TestCase):
    resource_availability: ResourceAvailabilityId = ResourceAvailabilityId.new_one()
    OWNER_ONE: Owner = Owner.new_one()
    OWNER_TWO: Owner = Owner.new_one()

    def test_can_be_blocked_when_is_available(self) -> None:
        # given
        resource_availability: ResourceAvailability = self._resource_availability()

        # when
        result: bool = resource_availability.block(self.OWNER_ONE)

        # then
        self.assertTrue(result)

    def test_cant_be_blocked_when_already_blocked_by_someone_else(self) -> None:
        # given
        resource_availability: ResourceAvailability = self._resource_availability()
        # and
        resource_availability.block(self.OWNER_ONE)

        # when
        result: bool = resource_availability.block(self.OWNER_TWO)

        # then
        self.assertFalse(result)

    def test_can_be_released_only_by_initial_owner(self) -> None:
        # given
        resource_availability: ResourceAvailability = self._resource_availability()
        # and
        resource_availability.block(self.OWNER_ONE)

        # when
        result: bool = resource_availability.release(self.OWNER_ONE)

        # then
        self.assertTrue(result)

    def test_cant_be_release_by_someone_else(self) -> None:
        # given
        resource_availability: ResourceAvailability = self._resource_availability()
        # and
        resource_availability.block(self.OWNER_ONE)

        # when
        result: bool = resource_availability.release(self.OWNER_TWO)

        # then
        self.assertFalse(result)

    def test_can_be_blocked_by_someone_else_after_releasing(self) -> None:
        # given
        resource_availability: ResourceAvailability = self._resource_availability()
        # and
        resource_availability.block(self.OWNER_ONE)
        # and
        resource_availability.release(self.OWNER_ONE)

        # when
        result: bool = resource_availability.release(self.OWNER_TWO)

        # then
        self.assertTrue(result)

    def test_can_disable_when_available(self) -> None:
        # given
        resource_availability: ResourceAvailability = self._resource_availability()

        # and
        result: bool = resource_availability.disable(self.OWNER_ONE)

        # then
        self.assertTrue(result)
        self.assertTrue(resource_availability.is_disabled())
        self.assertTrue(resource_availability.is_disabled_by(self.OWNER_ONE))

    def test_can_disable_when_blocked(self) -> None:
        # given
        resource_availability: ResourceAvailability = self._resource_availability()

        # and
        resultBlocking: bool = resource_availability.block(self.OWNER_ONE)

        # when
        resultDisabling: bool = resource_availability.disable(self.OWNER_TWO)

        # then
        self.assertTrue(resultBlocking)
        self.assertTrue(resultDisabling)
        self.assertTrue(resource_availability.is_disabled())
        self.assertTrue(resource_availability.is_disabled_by(self.OWNER_TWO))

    def test_cant_be_blocked_while_disabled(self) -> None:
        # given
        resource_availability: ResourceAvailability = self._resource_availability()

        # and
        resultDisabling: bool = resource_availability.disable(self.OWNER_ONE)

        # when
        resultBlocking: bool = resource_availability.block(self.OWNER_TWO)
        resultBlockingBySameOwner: bool = resource_availability.block(self.OWNER_ONE)

        # then
        self.assertTrue(resultDisabling)
        self.assertFalse(resultBlocking)
        self.assertFalse(resultBlockingBySameOwner)
        self.assertTrue(resource_availability.is_disabled())
        self.assertTrue(resource_availability.is_disabled_by(self.OWNER_ONE))

    def test_can_be_enabled_by_initial_requester(self) -> None:
        # given
        resource_availability: ResourceAvailability = self._resource_availability()

        # and
        resource_availability.disable(self.OWNER_ONE)

        # and
        result: bool = resource_availability.enable(self.OWNER_ONE)

        # then
        self.assertTrue(result)
        self.assertFalse(resource_availability.is_disabled())
        self.assertFalse(resource_availability.is_disabled_by(self.OWNER_ONE))

    def test_cant_be_enabled_by_another_requester(self) -> None:
        # given
        resource_availability: ResourceAvailability = self._resource_availability()

        # and
        resource_availability.disable(self.OWNER_ONE)

        # and
        result: bool = resource_availability.enable(self.OWNER_TWO)

        # then
        self.assertFalse(result)
        self.assertTrue(resource_availability.is_disabled())
        self.assertTrue(resource_availability.is_disabled_by(self.OWNER_ONE))

    def test_can_be_blocked_again_after_enabling(self) -> None:
        # given
        resource_availability: ResourceAvailability = self._resource_availability()

        # and
        resource_availability.disable(self.OWNER_ONE)

        # and
        resource_availability.enable(self.OWNER_ONE)

        # when
        result: bool = resource_availability.block(self.OWNER_TWO)

        # then
        self.assertTrue(result)

    def _resource_availability(self) -> ResourceAvailability:
        return ResourceAvailability(
            self.resource_availability,
            ResourceAvailabilityId.new_one(),
            TimeSlot.create_daily_time_slot_at_utc(2000, 1, 1),
        )
