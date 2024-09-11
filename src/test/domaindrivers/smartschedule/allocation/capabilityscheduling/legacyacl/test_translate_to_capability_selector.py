import uuid
from unittest import TestCase

from domaindrivers.smartschedule.allocation.capabilityscheduling.legacyacl.employee_created_in_legacy_system_message_handler import (
    EmployeeDataFromLegacyEsbMessage,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.legacyacl.translate_to_capability_selector import (
    TranslateToCapabilitySelector,
)
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.capability_selector import CapabilitySelector
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestTranslateToCapabilitySelector(TestCase):
    def test_translate_legacy_esb_message_to_capability_selector_model(self) -> None:
        # given
        legacy_permissions: list[str] = ["ADMIN<>2", "ROOT<>1"]
        legacy_skills_performed_together: list[list[str]] = [["JAVA", "CSHARP", "PYTHON"], ["RUST", "CSHARP", "PYTHON"]]
        legacy_exclusive_skills: list[str] = ["YT DRAMA COMMENTS"]

        # when
        result: list[CapabilitySelector] = self.translate(
            legacy_skills_performed_together, legacy_exclusive_skills, legacy_permissions
        )

        # then
        for capability in (
            CapabilitySelector.can_perform_one_of({Capability.skill("YT DRAMA COMMENTS")}),
            CapabilitySelector.can_perform_all_at_the_time(Capability.skills("JAVA", "CSHARP", "PYTHON")),
            CapabilitySelector.can_perform_all_at_the_time(Capability.skills("RUST", "CSHARP", "PYTHON")),
            CapabilitySelector.can_perform_one_of({Capability.permission("ADMIN")}),
            CapabilitySelector.can_perform_one_of({Capability.permission("ADMIN")}),
            CapabilitySelector.can_perform_one_of({Capability.permission("ROOT")}),
        ):
            self.assertIn(capability, result)

    def test_zero_means_no_permission_nowhere(self) -> None:
        legacy_permissions: list[str] = ["ADMIN<>0"]

        # when
        result: list[CapabilitySelector] = self.translate([], [], legacy_permissions)

        # then
        self.assertFalse(result)

    def translate(
        self,
        legacy_skills_performed_together: list[list[str]],
        legacy_exclusive_skills: list[str],
        legacy_permissions: list[str],
    ) -> list[CapabilitySelector]:
        return TranslateToCapabilitySelector().translate(
            EmployeeDataFromLegacyEsbMessage(
                uuid.uuid4(),
                legacy_skills_performed_together,
                legacy_exclusive_skills,
                legacy_permissions,
                TimeSlot.empty(),
            )
        )
