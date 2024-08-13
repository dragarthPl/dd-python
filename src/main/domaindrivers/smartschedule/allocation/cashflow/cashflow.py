from attr import define
from domaindrivers.smartschedule.allocation.cashflow.cost import Cost
from domaindrivers.smartschedule.allocation.cashflow.earnings import Earnings
from domaindrivers.smartschedule.allocation.cashflow.income import Income
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId


@define(slots=False)
class Cashflow:
    # @EmbeddedId
    _project_id: ProjectAllocationsId

    # @Embedded
    _income_value: Income

    # @Embedded
    _cost_value: Cost

    def __init__(self, project_id: ProjectAllocationsId, income: Income = None, cost: Cost = None) -> None:
        self._project_id = project_id
        self._income_value = income or Income.of_int(0)
        self._cost_value = cost or Cost.of(0)

    def earnings(self) -> Earnings:
        return self._income_value.minus(self._cost_value)

    def update(self, income: Income, cost: Cost) -> None:
        self._income_value = income
        self._cost_value = cost
