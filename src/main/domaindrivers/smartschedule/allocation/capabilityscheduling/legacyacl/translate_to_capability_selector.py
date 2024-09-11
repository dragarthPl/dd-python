from __future__ import annotations

from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.capability_selector import CapabilitySelector


class TranslateToCapabilitySelector:
    def translate(
        self,
        message: "EmployeeDataFromLegacyEsbMessage",  # type: ignore # noqa: F821
    ) -> list[CapabilitySelector]:
        employee_skills: list[CapabilitySelector] = list(
            map(
                lambda skills: CapabilitySelector.can_perform_all_at_the_time(set(map(Capability.skill, skills))),
                message.skills_performed_together,
            )
        )
        employee_exclusive_skills: list[CapabilitySelector] = list(
            map(lambda skill: CapabilitySelector.can_just_perform(Capability.skill(skill)), message.exclusive_skills)
        )
        employee_permissions: list[CapabilitySelector] = [
            perm for perms in map(self.__multiple_permission, message.permissions) for perm in perms
        ]
        # schedule or rewrite if exists;
        return employee_skills + employee_exclusive_skills + employee_permissions

    def __multiple_permission(self, permission_legacy_code: str) -> list[CapabilitySelector]:
        parts: list[str] = permission_legacy_code.split("<>")
        permission: str = parts[0]
        times: int = int(parts[1])
        return [CapabilitySelector.can_just_perform(Capability.permission(permission)) for _ in range(times)]
