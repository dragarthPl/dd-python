from typing import Final

from domaindrivers.smartschedule.allocation.cashflow.cashflow import Cashflow
from domaindrivers.smartschedule.allocation.cashflow.cashflow_repository import CashflowRepository
from domaindrivers.smartschedule.allocation.cashflow.cost import Cost
from domaindrivers.smartschedule.allocation.cashflow.earnings import Earnings
from domaindrivers.smartschedule.allocation.cashflow.income import Income
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from sqlalchemy.orm import Session


class CashFlowFacade:
    __session: Session
    __cashflow_repository: Final[CashflowRepository]

    def __init__(self, session: Session, cashflow_repository: CashflowRepository):
        self.__session: Session = session
        self.__cashflow_repository = cashflow_repository

    def add_income_and_cost(self, project_id: ProjectAllocationsId, income: Income, cost: Cost) -> None:
        cashflow: Cashflow = self.__cashflow_repository.find_by_id(project_id).or_else_get(
            lambda: Cashflow(project_id=project_id)
        )
        cashflow.update(income, cost)
        self.__cashflow_repository.save(cashflow)

    def find(self, project_id: ProjectAllocationsId) -> Earnings:
        by_id: Cashflow = self.__cashflow_repository.find_by_id(project_id).or_else_throw()
        return by_id.earnings()
