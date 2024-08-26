from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from unittest import TestCase

from domaindrivers.smartschedule.resource.employees.employee_facade import EmployeeFacade
from domaindrivers.smartschedule.resource.employees.employee_id import EmployeeId
from domaindrivers.smartschedule.resource.employees.employee_summary import EmployeeSummary
from domaindrivers.smartschedule.resource.employees.seniority import Seniority
from domaindrivers.smartschedule.shared.capability.capability import Capability


class TestCreatingEmployee(TestCase):
    SQL_SCRIPTS: tuple[str] = ("schema-resources.sql",)
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)

    employee_facade: EmployeeFacade

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.employee_facade = dependency_resolver.resolve_dependency(EmployeeFacade)

    def test_can_create_and_load_employee(self) -> None:
        # given
        employee: EmployeeId = self.employee_facade.add_employee(
            "resourceName",
            "lastName",
            Seniority.SENIOR,
            Capability.skills("JAVA, PYTHON"),
            Capability.permissions("ADMIN, COURT"),
        )

        # when
        loaded: EmployeeSummary = self.employee_facade.find_employee(employee)

        # then
        for skill in Capability.skills("JAVA, PYTHON"):
            self.assertIn(skill, loaded.skills)
        self.assertEqual(Capability.permissions("ADMIN, COURT"), loaded.permissions)
        self.assertEqual("resourceName", loaded.name)
        self.assertEqual("lastName", loaded.last_name)
        self.assertEqual(Seniority.SENIOR, loaded.seniority)

    def test_can_find_all_capabilities(self) -> None:
        # given
        self.employee_facade.add_employee(
            "staszek",
            "lastName",
            Seniority.SENIOR,
            Capability.skills("JAVA12", "PYTHON21"),
            Capability.permissions("ADMIN1", "COURT1"),
        )
        self.employee_facade.add_employee(
            "leon",
            "lastName",
            Seniority.SENIOR,
            Capability.skills("JAVA12", "PYTHON21"),
            Capability.permissions("ADMIN2", "COURT2"),
        )
        self.employee_facade.add_employee(
            "sławek",
            "lastName",
            Seniority.SENIOR,
            Capability.skills("JAVA12", "PYTHON21"),
            Capability.permissions("ADMIN3", "COURT3"),
        )

        # when
        loaded: list[Capability] = self.employee_facade.find_all_capabilities()

        # then
        for asset in (
            Capability.permission("ADMIN1"),
            Capability.permission("ADMIN2"),
            Capability.permission("ADMIN3"),
            Capability.permission("COURT1"),
            Capability.permission("COURT2"),
            Capability.permission("COURT3"),
            Capability.skill("JAVA12"),
            Capability.skill("JAVA12"),
            Capability.skill("JAVA12"),
            Capability.skill("PYTHON21"),
            Capability.skill("PYTHON21"),
            Capability.skill("PYTHON21"),
        ):
            self.assertIn(asset, loaded)
