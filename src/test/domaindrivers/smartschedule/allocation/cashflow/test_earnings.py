from decimal import Decimal
from unittest import TestCase

from domaindrivers.smartschedule.allocation.cashflow.cost import Cost
from domaindrivers.smartschedule.allocation.cashflow.earnings import Earnings
from domaindrivers.smartschedule.allocation.cashflow.income import Income

TEN = Decimal(10)


class TestEarnings(TestCase):
    def test_income_minus_cost_test(self) -> None:
        # expect
        self.assertEqual(Earnings.of(9), Income.of_decimal(TEN).minus(Cost.of(1)))
        self.assertEqual(Earnings.of(8), Income.of_decimal(TEN).minus(Cost.of(2)))
        self.assertEqual(Earnings.of(7), Income.of_decimal(TEN).minus(Cost.of(3)))
        self.assertEqual(Earnings.of(-70), Income.of_int(100).minus(Cost.of(170)))

    def test_greater_than_test(self) -> None:
        self.assertTrue(Earnings.of(10).greater_than(Earnings.of(9)))
        self.assertTrue(Earnings.of(10).greater_than(Earnings.of(0)))
        self.assertTrue(Earnings.of(10).greater_than(Earnings.of(-1)))
        self.assertFalse(Earnings.of(10).greater_than(Earnings.of(10)))
        self.assertFalse(Earnings.of(10).greater_than(Earnings.of(11)))
