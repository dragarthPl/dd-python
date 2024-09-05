from typing import Final
from unittest import TestCase

from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.capability_selector import CapabilitySelector


class TestCapabilitySelector(TestCase):
    RUST: Final[Capability] = Capability("RUST", "SKILL")
    BEING_AN_ADMIN: Final[Capability] = Capability("ADMIN", "PERMISSION")
    JAVA: Final[Capability] = Capability("JAVA", "SKILL")

    def test_allocatable_resource_can_perform_only_one_of_present_capabilities(self) -> None:
        # given
        admin_or_rust: CapabilitySelector = CapabilitySelector.can_perform_one_of({self.BEING_AN_ADMIN, self.RUST})

        # expect
        self.assertTrue(admin_or_rust.can_perform(self.BEING_AN_ADMIN))
        self.assertTrue(admin_or_rust.can_perform(self.RUST))
        self.assertFalse(admin_or_rust.can_perform_capabilities({self.RUST, self.BEING_AN_ADMIN}))
        self.assertFalse(admin_or_rust.can_perform(Capability("JAVA", "SKILL")))
        self.assertFalse(admin_or_rust.can_perform(Capability("LAWYER", "PERMISSION")))

    def test_allocatable_resource_can_perform_simultaneous_capabilities(self) -> None:
        # given
        admin_and_rust: CapabilitySelector = CapabilitySelector.can_perform_all_at_the_time(
            {self.BEING_AN_ADMIN, self.RUST}
        )

        # expect
        self.assertTrue(admin_and_rust.can_perform(self.BEING_AN_ADMIN))
        self.assertTrue(admin_and_rust.can_perform(self.RUST))
        self.assertTrue(admin_and_rust.can_perform_capabilities({self.RUST, self.BEING_AN_ADMIN}))
        self.assertFalse(admin_and_rust.can_perform_capabilities({self.RUST, self.BEING_AN_ADMIN, self.JAVA}))
        self.assertFalse(admin_and_rust.can_perform(self.JAVA))
        self.assertFalse(admin_and_rust.can_perform(Capability("LAWYER", "PERMISSION")))
