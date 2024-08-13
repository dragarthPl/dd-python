from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from unittest import TestCase

from domaindrivers.smartschedule.allocation.cashflow.cash_flow_facade import CashFlowFacade
from domaindrivers.smartschedule.allocation.cashflow.cost import Cost
from domaindrivers.smartschedule.allocation.cashflow.earnings import Earnings
from domaindrivers.smartschedule.allocation.cashflow.income import Income
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId


class TestCashFlowFacade(TestCase):
    SQL_SCRIPTS: tuple[str] = ("schema-cashflow.sql",)
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)
    cash_flow_facade: CashFlowFacade

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.cash_flow_facade = dependency_resolver.resolve_dependency(CashFlowFacade)

    def test_can_save_cash_flow(self) -> None:
        # given
        project_id: ProjectAllocationsId = ProjectAllocationsId.new_one()

        # when
        self.cash_flow_facade.add_income_and_cost(project_id, Income.of_int(100), Cost.of(50))

        # then
        self.assertEqual(Earnings.of(50), self.cash_flow_facade.find(project_id))
