from unittest import TestCase

from domaindrivers.smartschedule.resource.employees.employee_allocation_policy import (
    CompositePolicy,
    DefaultPolicy,
    EmployeeAllocationPolicy,
    OneOfSkills,
    PermissionsInMultipleProjects,
)
from domaindrivers.smartschedule.resource.employees.employee_id import EmployeeId
from domaindrivers.smartschedule.resource.employees.employee_summary import EmployeeSummary
from domaindrivers.smartschedule.resource.employees.seniority import Seniority
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.capability_selector import CapabilitySelector


class TestAllocationPolicies(TestCase):
    def test_default_policy_should_return_just_one_skill_at_once(self) -> None:
        # given
        employee: EmployeeSummary = EmployeeSummary(
            EmployeeId.new_one(),
            "resourceName",
            "lastName",
            Seniority.LEAD,
            Capability.skills("JAVA"),
            Capability.permissions("ADMIN"),
        )

        # when
        capabilities: list[CapabilitySelector] = DefaultPolicy().simultaneous_capabilities_of(employee)

        # then
        self.assertEqual(len(capabilities), 1)
        self.assertEqual(capabilities[0].capabilities, {Capability.skill("JAVA"), Capability.permission("ADMIN")})

    def test_permissions_can_be_shared_between_projects(self) -> None:
        # given
        policy: EmployeeAllocationPolicy = PermissionsInMultipleProjects(3)
        employee: EmployeeSummary = EmployeeSummary(
            EmployeeId.new_one(),
            "resourceName",
            "lastName",
            Seniority.LEAD,
            Capability.skills("JAVA"),
            Capability.permissions("ADMIN"),
        )

        # when
        capabilities: list[CapabilitySelector] = policy.simultaneous_capabilities_of(employee)

        # then
        self.assertEqual(len(capabilities), 3)
        for capability in capabilities:
            self.assertEqual(capability.capabilities, {Capability.permission("ADMIN")})

    def test_can_create_composite_policy(self) -> None:
        # given
        policy: CompositePolicy = CompositePolicy([PermissionsInMultipleProjects(3), OneOfSkills()])
        employee: EmployeeSummary = EmployeeSummary(
            EmployeeId.new_one(),
            "resourceName",
            "lastName",
            Seniority.LEAD,
            Capability.skills("JAVA", "PYTHON"),
            Capability.permissions("ADMIN"),
        )

        # when
        capabilities: list[CapabilitySelector] = policy.simultaneous_capabilities_of(employee)

        # then
        self.assertEqual(len(capabilities), 4)

        java_python_counter = 0
        admin_counter = 0
        for capability in capabilities:
            if Capability.skills("JAVA", "PYTHON") == capability.capabilities:
                java_python_counter += 1
            elif Capability.permission("ADMIN") in capability.capabilities:
                admin_counter += 1

        self.assertEqual(java_python_counter, 1)
        self.assertEqual(admin_counter, 3)
