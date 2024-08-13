import hashlib
from decimal import Decimal
from typing import Any

from attr import field, frozen
from domaindrivers.smartschedule.allocation.cashflow.cost import Cost
from domaindrivers.smartschedule.allocation.cashflow.earnings import Earnings


@frozen
class Income:
    income: Decimal = field(default=None)

    def __composite_values__(self) -> tuple[Decimal]:
        return (self.income,)

    @classmethod
    def of_decimal(cls, decimal: Decimal) -> "Income":
        return cls(decimal)

    @classmethod
    def of_int(cls, integer: int) -> "Income":
        return cls(Decimal(integer))

    def __eq__(self, other: Any) -> bool:
        if other is None or not isinstance(other, Income):
            return False
        return bool(self.income == other.income)

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.income).encode("utf-8"))

        return int(m.hexdigest(), 16)

    def minus(self, estimated_costs: Cost) -> Earnings:
        return Earnings(self.income - estimated_costs.value())
