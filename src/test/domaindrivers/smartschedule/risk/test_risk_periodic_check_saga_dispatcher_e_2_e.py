import uuid
from datetime import datetime, timedelta
from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from typing import Callable
from unittest import TestCase

import mockito
import pytz
from domaindrivers.smartschedule.allocation.allocation_facade import AllocationFacade
from domaindrivers.smartschedule.allocation.capabilities_allocated import CapabilitiesAllocated
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capabilities_summary import (
    AllocatableCapabilitiesSummary,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.cashflow.cash_flow_facade import CashFlowFacade
from domaindrivers.smartschedule.allocation.cashflow.cost import Cost
from domaindrivers.smartschedule.allocation.cashflow.earnings import Earnings
from domaindrivers.smartschedule.allocation.cashflow.earnings_recalculated import EarningsRecalculated
from domaindrivers.smartschedule.allocation.cashflow.income import Income
from domaindrivers.smartschedule.allocation.demand import Demand
from domaindrivers.smartschedule.allocation.demands import Demands
from domaindrivers.smartschedule.allocation.project_allocation_scheduled import ProjectAllocationScheduled
from domaindrivers.smartschedule.allocation.project_allocations_demands_scheduled import (
    ProjectAllocationsDemandsScheduled,
)
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.availability.owner import Owner
from domaindrivers.smartschedule.availability.resource_id import ResourceId
from domaindrivers.smartschedule.availability.resource_taken_over import ResourceTakenOver
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.smartschedule.resource.employees.employee_facade import EmployeeFacade
from domaindrivers.smartschedule.resource.employees.employee_id import EmployeeId
from domaindrivers.smartschedule.resource.employees.seniority import Seniority
from domaindrivers.smartschedule.risk.risk_periodic_check_saga_dispatcher import RiskPeriodicCheckSagaDispatcher
from domaindrivers.smartschedule.risk.risk_push_notification import RiskPushNotification
from domaindrivers.smartschedule.shared.capability.capability import Capability
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from freezegun import freeze_time
from mockito import arg_that, eq, mock


class TestRiskPeriodicCheckSagaDispatcherE2E(TestCase):
    ONE_DAY_LONG: TimeSlot = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
    PROJECT_DATES: TimeSlot = TimeSlot(datetime.now(pytz.UTC), datetime.now(pytz.UTC) + timedelta(days=20))

    SQL_SCRIPTS: tuple[str, ...] = (
        "schema-planning.sql",
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
            ProjectAllocationsDemandsScheduled.of(project_id, Demands.of(java_one_day_demand), datetime.now(pytz.UTC))
        )

        # when
        self.risk_saga_dispatcher.handle(
            CapabilitiesAllocated.of(uuid.uuid4(), project_id, Demands.none(), datetime.now(pytz.UTC))
        )

        # then
        mockito.verify(self.risk_push_notification).notify_demands_satisfied(project_id)

    def test_informs_about_potential_risk_when_resource_taken_over(self) -> None:
        # given
        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        java: Capability = Capability.skill("JAVA-MID-JUNIOR")
        java_one_day_demand: Demand = Demand(java, self.ONE_DAY_LONG)
        # and
        self.risk_saga_dispatcher.handle(
            ProjectAllocationsDemandsScheduled.of(project_id, Demands.of(java_one_day_demand), datetime.now(pytz.utc))
        )
        # and
        self.risk_saga_dispatcher.handle(
            CapabilitiesAllocated.of(uuid.uuid4(), project_id, Demands.none(), datetime.now(pytz.utc))
        )
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

    def test_weekly_check_does_nothing_when_not_close_to_deadline_and_demands_not_satisfied(self) -> None:
        # given
        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        java: Capability = Capability.skill("JAVA-MID-JUNIOR")
        java_one_day_demand: Demand = Demand(java, self.ONE_DAY_LONG)
        # and
        self.risk_saga_dispatcher.handle(
            ProjectAllocationsDemandsScheduled.of(project_id, Demands.of(java_one_day_demand), datetime.now(pytz.UTC))
        )
        # and
        self.risk_saga_dispatcher.handle(
            ProjectAllocationScheduled.of(project_id, self.PROJECT_DATES, datetime.now(pytz.UTC))
        )

        # when
        with freeze_time(self.days_before_deadline(100)):
            self.risk_saga_dispatcher.handle_weekly_check()

            # then
            mockito.verifyNoMoreInteractions(self.risk_push_notification)

    def test_weekly_check_does_nothing_when_close_to_deadline_and_demands_satisfied(self) -> None:
        # given
        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        java: Capability = Capability.skill("JAVA-MID-JUNIOR-UNIQUE")
        java_one_day_demand: Demand = Demand(java, self.ONE_DAY_LONG)
        self.risk_saga_dispatcher.handle(
            ProjectAllocationsDemandsScheduled.of(project_id, Demands.of(java_one_day_demand), datetime.now(pytz.UTC))
        )
        # and
        self.risk_saga_dispatcher.handle(EarningsRecalculated.of(project_id, Earnings.of(10), datetime.now(pytz.UTC)))
        # and
        self.risk_saga_dispatcher.handle(
            CapabilitiesAllocated.of(uuid.uuid4(), project_id, Demands.none(), datetime.now(pytz.UTC))
        )
        # and
        self.risk_saga_dispatcher.handle(
            ProjectAllocationScheduled.of(project_id, self.PROJECT_DATES, datetime.now(pytz.UTC))
        )

        # when
        with freeze_time(self.days_before_deadline(100)):
            self.mockito_reset()
            self.risk_saga_dispatcher.handle_weekly_check()

            # then
            mockito.verifyNoMoreInteractions(self.risk_push_notification)

    def test_find_replacements_when_deadline_close(self) -> None:
        # given
        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        java: Capability = Capability.skill("JAVA-MID-JUNIOR")
        java_one_day_demand: Demand = Demand(java, self.ONE_DAY_LONG)
        self.risk_saga_dispatcher.handle(
            ProjectAllocationsDemandsScheduled.of(project_id, Demands.of(java_one_day_demand), datetime.now(pytz.UTC))
        )
        # and
        self.risk_saga_dispatcher.handle(EarningsRecalculated.of(project_id, Earnings.of(10), datetime.now(pytz.UTC)))
        # and
        self.risk_saga_dispatcher.handle(
            ProjectAllocationScheduled.of(project_id, self.PROJECT_DATES, datetime.now(pytz.UTC))
        )
        # and
        employee: AllocatableCapabilityId = self.there_is_employee_with_skills({java}, self.ONE_DAY_LONG)

        # when
        self.mockito_reset()
        with freeze_time(self.days_before_deadline(20)):
            self.risk_saga_dispatcher.handle_weekly_check()

            # then
            mockito.verify(self.risk_push_notification).notify_about_availability(
                eq(project_id), arg_that(self.employee_was_suggested_for_demand(java_one_day_demand, employee))
            )

    def test_suggest_resources_from_different_projects(self) -> None:
        # given
        high_value_project: ProjectAllocationsId = ProjectAllocationsId.new_one()
        low_value_project: ProjectAllocationsId = ProjectAllocationsId.new_one()
        # and
        java: Capability = Capability.skill("JAVA-MID-JUNIOR-SUPER-UNIQUE")
        java_one_day_demand: Demand = Demand(java, self.ONE_DAY_LONG)
        # and
        self.allocation_facade.schedule_project_allocation_demands(high_value_project, Demands.of(java_one_day_demand))
        self.cash_flow_facade.add_income_and_cost(high_value_project, Income.of_int(10000), Cost.of(10))
        self.allocation_facade.schedule_project_allocation_demands(low_value_project, Demands.of(java_one_day_demand))
        self.cash_flow_facade.add_income_and_cost(low_value_project, Income.of_int(100), Cost.of(10))
        # and
        employee: AllocatableCapabilityId = self.there_is_employee_with_skills({java}, self.ONE_DAY_LONG)
        self.allocation_facade.allocate_to_project(low_value_project, employee, self.ONE_DAY_LONG)
        # and
        self.risk_saga_dispatcher.handle(
            ProjectAllocationScheduled.of(high_value_project, self.PROJECT_DATES, datetime.now(pytz.UTC))
        )

        # when
        self.mockito_reset()
        self.allocation_facade.edit_project_dates(high_value_project, self.PROJECT_DATES)
        self.allocation_facade.edit_project_dates(low_value_project, self.PROJECT_DATES)
        with freeze_time(self.days_before_deadline(1)):
            self.risk_saga_dispatcher.handle_weekly_check()

            # then
            mockito.verify(self.risk_push_notification).notify_profitable_relocation_found(high_value_project, employee)

    def employee_was_suggested_for_demand(
        self, demand: Demand, allocatable_capability_id: AllocatableCapabilityId
    ) -> Callable[[dict[Demand, AllocatableCapabilitiesSummary]], bool]:
        return lambda suggestions: any(
            suggestion.allocatable_capability_id == allocatable_capability_id
            for suggestion in suggestions.get(demand).all
        )

    def there_is_employee_with_skills(self, skills: set[Capability], in_slot: TimeSlot) -> AllocatableCapabilityId:
        staszek: EmployeeId = self.employee_facade.add_employee(
            "Staszek", "Staszkowski", Seniority.MID, skills, Capability.permissions()
        )
        allocatable_capability_ids: list[AllocatableCapabilityId] = self.employee_facade.schedule_capabilities(
            staszek, in_slot
        )
        assert len(allocatable_capability_ids) == 1
        return allocatable_capability_ids[0]

    def days_before_deadline(self, days: int) -> datetime:
        return self.PROJECT_DATES.to - timedelta(days=days)
