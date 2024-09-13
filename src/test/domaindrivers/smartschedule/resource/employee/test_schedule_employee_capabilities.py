from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from unittest import TestCase

from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capabilities_summary import (
    AllocatableCapabilitiesSummary,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.capability_finder import CapabilityFinder
from domaindrivers.smartschedule.resource.employees.employee_facade import EmployeeFacade
from domaindrivers.smartschedule.resource.employees.employee_id import EmployeeId
from domaindrivers.smartschedule.resource.employees.seniority import Seniority
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot


class TestScheduleEmployeeCapabilities(TestCase):
    SQL_SCRIPTS: tuple[str, ...] = (
        "schema-resources.sql",
        "schema-availability.sql",
        "schema-capability-scheduling.sql",
    )
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)
    employee_facade: EmployeeFacade
    capability_finder: CapabilityFinder

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.employee_facade = dependency_resolver.resolve_dependency(EmployeeFacade)
        self.capability_finder = dependency_resolver.resolve_dependency(CapabilityFinder)

    def test_can_setup_capabilities_according_to_policy(self) -> None:
        # given
        employee: EmployeeId = self.employee_facade.add_employee(
            "resourceName",
            "lastName",
            Seniority.LEAD,
            Capability.skills("JAVA, PYTHON"),
            Capability.permissions("ADMIN"),
        )
        # when
        one_day: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        allocations: list[AllocatableCapabilityId] = self.employee_facade.schedule_capabilities(employee, one_day)

        # then
        loaded: AllocatableCapabilitiesSummary = self.capability_finder.find_by_id(allocations)
        self.assertEqual(len(allocations), len(loaded.all))
