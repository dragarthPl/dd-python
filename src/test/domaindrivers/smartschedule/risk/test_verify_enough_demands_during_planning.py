from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from unittest import TestCase

import mockito
from domaindrivers.smartschedule.planning.demand import Demand
from domaindrivers.smartschedule.planning.demands import Demands
from domaindrivers.smartschedule.planning.planning_facade import PlanningFacade
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.resource.employees.employee_facade import EmployeeFacade
from domaindrivers.smartschedule.resource.employees.seniority import Seniority
from domaindrivers.smartschedule.risk.risk_push_notification import RiskPushNotification
from domaindrivers.smartschedule.risk.verify_enough_demands_during_planning import VerifyEnoughDemandsDuringPlanning
from domaindrivers.smartschedule.shared.capability.capability import Capability
from mockito import never


class TestVerifyEnoughDemandsDuringPlanning(TestCase):
    SQL_SCRIPTS: tuple[str, ...] = (
        "schema-planning.sql",
        "schema-availability.sql",
        "schema-resources.sql",
        "schema-risk.sql",
    )
    test_db_configuration: TestDbConfiguration

    dependency_resolver: DependencyResolverForTest
    risk_push_notification: RiskPushNotification
    verify_enough_demands_during_planning: VerifyEnoughDemandsDuringPlanning
    employee_facade: EmployeeFacade
    planning_facade: PlanningFacade

    def setUp(self) -> None:
        self.test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=self.SQL_SCRIPTS)
        self.dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.risk_push_notification = self.dependency_resolver.resolve_dependency(RiskPushNotification)
        self.verify_enough_demands_during_planning = self.dependency_resolver.resolve_dependency(
            VerifyEnoughDemandsDuringPlanning
        )
        self.verify_enough_demands_during_planning._VerifyEnoughDemandsDuringPlanning__risk_push_notification = (  # type: ignore[attr-defined]
            mockito.mock()
        )
        self.employee_facade = self.dependency_resolver.resolve_dependency(EmployeeFacade)
        self.planning_facade = self.dependency_resolver.resolve_dependency(PlanningFacade)

    def test_does_nothing_when_enough_resources(self) -> None:
        # given
        self.employee_facade.add_employee(
            "resourceName", "lastName", Seniority.SENIOR, Capability.skills("JAVA5", "PYTHON"), Capability.permissions()
        )
        self.employee_facade.add_employee(
            "resourceName", "lastName", Seniority.SENIOR, Capability.skills("C#", "RUST"), Capability.permissions()
        )
        # and
        project_id: ProjectId = self.planning_facade.add_new_project_with_stages("java5")

        # when
        self.planning_facade.add_demands(project_id, Demands.of(Demand(Capability.skill("JAVA5"))))

        #  then
        mockito.verify(
            self.verify_enough_demands_during_planning._VerifyEnoughDemandsDuringPlanning__risk_push_notification,
            never,  # type: ignore[attr-defined]
        ).notify_about_possible_risk_during_planning(
            project_id, Demands.of(Demand.demand_for(Capability.skill("JAVA")))
        )

    def test_notifies_when_not_enough_resources(self) -> None:
        # given
        self.employee_facade.add_employee(
            "resourceName", "lastName", Seniority.SENIOR, Capability.skills("JAVA"), Capability.permissions()
        )
        self.employee_facade.add_employee(
            "resourceName", "lastName", Seniority.SENIOR, Capability.skills("C"), Capability.permissions()
        )
        # and
        java: ProjectId = self.planning_facade.add_new_project_with_stages("java")
        c: ProjectId = self.planning_facade.add_new_project_with_stages("C")
        # and
        self.planning_facade.add_demands(java, Demands.of(Demand(Capability.skill("JAVA"))))
        self.planning_facade.add_demands(c, Demands.of(Demand(Capability.skill("C"))))
        # when
        rust: ProjectId = self.planning_facade.add_new_project_with_stages("rust")
        self.planning_facade.add_demands(rust, Demands.of(Demand(Capability.skill("RUST"))))

        # then
        mockito.verify(
            self.verify_enough_demands_during_planning._VerifyEnoughDemandsDuringPlanning__risk_push_notification  # type: ignore[attr-defined]
        ).notify_about_possible_risk_during_planning(rust, Demands.of(Demand.demand_for(Capability.skill("RUST"))))
