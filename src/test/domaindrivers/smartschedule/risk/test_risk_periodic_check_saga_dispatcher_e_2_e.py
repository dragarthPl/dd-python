from datetime import datetime, timedelta
from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from typing import Callable
from unittest import TestCase

import mockito
import pytz
from domaindrivers.smartschedule.allocation.allocation_facade import AllocationFacade
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capabilities_summary import (
    AllocatableCapabilitiesSummary,
)
from domaindrivers.smartschedule.allocation.cashflow.cash_flow_facade import CashFlowFacade
from domaindrivers.smartschedule.allocation.demand import Demand
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.not_satisfied_demands import NotSatisfiedDemands
from domaindrivers.smartschedule.allocation.project_allocation_scheduled import ProjectAllocationScheduled
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.availability.resource_taken_over import ResourceTakenOver
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.resource.employees.employee_facade import EmployeeFacade
from domaindrivers.smartschedule.resource.employees.employee_id import EmployeeId
from domaindrivers.smartschedule.risk.risk_periodic_check_saga_dispatcher import RiskPeriodicCheckSagaDispatcher
from domaindrivers.smartschedule.risk.risk_push_notification import RiskPushNotification
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from freezegun import freeze_time
from mockito import mock


class TestRiskPeriodicCheckSagaDispatcherE2E(TestCase):
    ONE_DAY_LONG: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
    PROJECT_DATES: TimeSlot = TimeSlot(datetime.now(pytz.UTC), datetime.now(pytz.UTC) + timedelta(days=20))

    SQL_SCRIPTS: tuple[str, ...] = (
        "schema-availability.sql",
        "schema-resources.sql",
        "schema-allocations.sql",
        "schema-risk.sql",
        "schema-cashflow.sql",
    )
    test_db_configuration: TestDbConfiguration

    dependency_resolver: DependencyResolverForTest

    employee_facade: EmployeeFacade
    allocation_facade: AllocationFacade
    risk_saga_dispatcher: RiskPeriodicCheckSagaDispatcher
    risk_push_notification: RiskPushNotification
    cash_flow_facade: CashFlowFacade

    def setUp(self) -> None:
        self.test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=self.SQL_SCRIPTS)
        self.dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.employee_facade = self.dependency_resolver.resolve_dependency(EmployeeFacade)
        self.allocation_facade = self.dependency_resolver.resolve_dependency(AllocationFacade)
        self.risk_saga_dispatcher = self.dependency_resolver.resolve_dependency(RiskPeriodicCheckSagaDispatcher)
        self.risk_saga_dispatcher._RiskPeriodicCheckSagaDispatcher__risk_push_notification = mock()  # type: ignore[attr-defined]
        self.risk_push_notification = self.risk_saga_dispatcher._RiskPeriodicCheckSagaDispatcher__risk_push_notification  # type: ignore[attr-defined]
        self.cash_flow_facade = self.dependency_resolver.resolve_dependency(CashFlowFacade)

    def mockito_reset(self) -> None:
        self.risk_saga_dispatcher._RiskPeriodicCheckSagaDispatcher__risk_push_notification = mock()  # type: ignore[attr-defined]
        self.risk_push_notification = self.risk_saga_dispatcher._RiskPeriodicCheckSagaDispatcher__risk_push_notification  # type: ignore[attr-defined]

    def test_informs_about_demand_satisfied(self) -> None:
        # given
        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        java: Capability = Capability.skill("JAVA-MID-JUNIOR")
        java_one_day_demand: Demand = Demand(java, self.ONE_DAY_LONG)
        # and
        self.risk_saga_dispatcher.handle(
            NotSatisfiedDemands.for_one_project(project_id, Demands.of(java_one_day_demand), datetime.now(pytz.UTC))
        )

        # when
        self.risk_saga_dispatcher.handle(NotSatisfiedDemands.all_satisfied(project_id, datetime.now(pytz.UTC)))

        # then
        mockito.verify(self.risk_push_notification).notify_demands_satisfied(project_id)

    def test_informs_about_demand_satisfied_for_all_projects(self) -> None:
        # given
        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        project_id_2: ProjectAllocationsId = ProjectAllocationsId.new_one()
        # and
        no_missing_demands: dict[ProjectAllocationsId, Demands] = {
            project_id: Demands.none(),
            project_id_2: Demands.none(),
        }
        # when
        self.risk_saga_dispatcher.handle(NotSatisfiedDemands.of(no_missing_demands, datetime.now(pytz.UTC)))

        # then
        mockito.verify(self.risk_push_notification).notify_demands_satisfied(project_id)
        mockito.verify(self.risk_push_notification).notify_demands_satisfied(project_id_2)

    def test_informs_about_potential_risk_when_resource_taken_over(self) -> None:
        # given
        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        java: Capability = Capability.skill("JAVA-MID-JUNIOR")
        java_one_day_demand: Demand = Demand(java, self.ONE_DAY_LONG)
        # and
        self.risk_saga_dispatcher.handle(
            NotSatisfiedDemands.for_one_project(project_id, Demands.of(java_one_day_demand), datetime.now(pytz.UTC))
        )
        # and
        self.risk_saga_dispatcher.handle(NotSatisfiedDemands.all_satisfied(project_id, datetime.now(pytz.UTC)))
        # and
        self.risk_saga_dispatcher.handle(
            ProjectAllocationScheduled.of(project_id, self.PROJECT_DATES, datetime.now(pytz.UTC))
        )

        # when
        self.mockito_reset()
        with freeze_time(self.days_before_deadline(100)):
            self.risk_saga_dispatcher.handle(
                ResourceTakenOver.of(
                    ResourceId.new_one(), {Owner.of(project_id.id())}, self.ONE_DAY_LONG, datetime.now(pytz.UTC)
                )
            )

            # then
            mockito.verify(self.risk_push_notification).notify_about_possible_risk(project_id)

    def test_does_nothing_when_resource_taken_over_from_from_unknown_project(self) -> None:
        # given
        unknown: ProjectId = ProjectId.new_one()
        # when
        self.risk_saga_dispatcher.handle(
            ResourceTakenOver.of(
                ResourceId.new_one(), {Owner.of(unknown.id())}, self.ONE_DAY_LONG, datetime.now(pytz.UTC)
            )
        )

        # then
        mockito.verifyNoMoreInteractions(self.risk_push_notification)

    def employee_was_suggested_for_demand(
        self, demand: Demand, employee: EmployeeId
    ) -> Callable[[dict[Demand, AllocatableCapabilitiesSummary]], bool]:
        return lambda suggestions: any(
            suggestion.allocatable_resource_id == employee.to_allocatable_resource_id
            for suggestion in suggestions.get(demand).all
        )

    def days_before_deadline(self, days: int) -> datetime:
        return self.PROJECT_DATES.to - timedelta(days=days)
