from attr import define
from attrs import field
from domaindrivers.smartschedule.allocation.cashflow.cost import Cost
from domaindrivers.smartschedule.allocation.cashflow.earnings import Earnings
from domaindrivers.smartschedule.allocation.cashflow.income import Income
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId


@define(slots=False)
class Cashflow:
    _project_id: ProjectAllocationsId = field(default=None)
    _income_value: Income = field(factory=lambda: Income.of_int(0))
    _cost_value: Cost = field(factory=lambda: Cost.of(0))

    def earnings(self) -> Earnings:
        return self._income_value.minus(self._cost_value)

    def update(self, income: Income, cost: Cost) -> None:
        self._income_value = income
        self._cost_value = cost
