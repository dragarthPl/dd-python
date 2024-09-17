from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from typing import Callable, cast, Type
from unittest import TestCase

from domaindrivers.smartschedule.allocation.cashflow.cash_flow_facade import CashFlowFacade
from domaindrivers.smartschedule.allocation.cashflow.cost import Cost
from domaindrivers.smartschedule.allocation.cashflow.earnings import Earnings
from domaindrivers.smartschedule.allocation.cashflow.income import Income
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.shared.event import Event
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher
from mockito import arg_that, mock, mockito


class TestCashFlowFacade(TestCase):
    SQL_SCRIPTS: tuple[str] = ("schema-cashflow.sql",)
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)
    cash_flow_facade: CashFlowFacade
    events_publisher: EventsPublisher

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.cash_flow_facade = dependency_resolver.resolve_dependency(CashFlowFacade)
        self.events_publisher = dependency_resolver.resolve_dependency(cast(Type[EventsPublisher], EventsPublisher))

    def test_can_save_cash_flow(self) -> None:
        # given
        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()

        # when
        self.cash_flow_facade.add_income_and_cost(project_id, Income.of_int(100), Cost.of(50))

        # then
        self.assertEqual(Earnings.of(50), self.cash_flow_facade.find(project_id))

    def test_updating_cash_flow_emits_an_event(self) -> None:
        # given
        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()
        income: Income = Income.of_int(100)
        cost: Cost = Cost.of(50)

        # when
        self.cash_flow_facade._CashFlowFacade__events_publisher = mock()  # type: ignore[attr-defined]
        self.cash_flow_facade.add_income_and_cost(project_id, income, cost)

        # then
        mockito.verify(self.cash_flow_facade._CashFlowFacade__events_publisher).publish(  # type: ignore[attr-defined]
            arg_that(self.is_earnings_recalculated_event(project_id, Earnings.of(50)))
        )

    def is_earnings_recalculated_event(
        self, project_id: ProjectAllocationsId, earnings: Earnings
    ) -> Callable[[Event], bool]:
        return (
            lambda event: getattr(event, "project_id") == project_id
            and getattr(event, "earnings") == earnings
            and event.occurred_at() is not None
        )
