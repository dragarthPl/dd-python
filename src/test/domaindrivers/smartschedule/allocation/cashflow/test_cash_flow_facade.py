from datetime import datetime
from test.domaindrivers.smartschedule.allocation.cashflow.cash_flow_test_configuration import CashFlowTestConfiguration
from typing import Callable, Final
from unittest import TestCase

import mockito
from domaindrivers.smartschedule.allocation.cashflow.cash_flow_facade import CashFlowFacade
from domaindrivers.smartschedule.allocation.cashflow.cost import Cost
from domaindrivers.smartschedule.allocation.cashflow.earnings import Earnings
from domaindrivers.smartschedule.allocation.cashflow.income import Income
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher
from domaindrivers.smartschedule.shared.published_event import PublishedEvent
from mockito import arg_that, mock


class TestCashFlowFacade(TestCase):
    NOW: Final[datetime] = datetime.now()

    events_publisher: EventsPublisher
    cash_flow_facade: CashFlowFacade

    def setUp(self) -> None:
        self.events_publisher = mock()
        self.cash_flow_facade = CashFlowTestConfiguration.cash_flow_facade(self.events_publisher)

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
    ) -> Callable[[PublishedEvent], bool]:
        return (
            lambda event: getattr(event, "project_id") == project_id
            and getattr(event, "earnings") == earnings
            and event.occurred_at() is not None
        )
