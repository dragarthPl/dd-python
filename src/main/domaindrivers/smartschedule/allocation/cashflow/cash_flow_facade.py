from datetime import datetime
from typing import Final

import pytz
from domaindrivers.smartschedule.allocation.cashflow.cashflow import Cashflow
from domaindrivers.smartschedule.allocation.cashflow.cashflow_repository import CashflowRepository
from domaindrivers.smartschedule.allocation.cashflow.cost import Cost
from domaindrivers.smartschedule.allocation.cashflow.earnings import Earnings
from domaindrivers.smartschedule.allocation.cashflow.earnings_recalculated import EarningsRecalculated
from domaindrivers.smartschedule.allocation.cashflow.income import Income
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher
from sqlalchemy.orm import Session


class CashFlowFacade:
    __session: Session
    __cashflow_repository: Final[CashflowRepository]
    __events_publisher: Final[EventsPublisher]

    def __init__(self, session: Session, cashflow_repository: CashflowRepository, events_publisher: EventsPublisher):
        self.__session: Session = session
        self.__cashflow_repository = cashflow_repository
        self.__events_publisher = events_publisher

    def add_income_and_cost(self, project_id: ProjectAllocationsId, income: Income, cost: Cost) -> None:
        cashflow: Cashflow = self.__cashflow_repository.find_by_id(project_id).or_else_get(lambda: Cashflow(project_id))
        cashflow.update(income, cost)
        self.__events_publisher.publish(
            EarningsRecalculated.of(project_id, cashflow.earnings(), datetime.now(pytz.UTC))
        )
        self.__cashflow_repository.save(cashflow)

    def find(self, project_id: ProjectAllocationsId) -> Earnings:
        by_id: Cashflow = self.__cashflow_repository.find_by_id(project_id).or_else_throw()
        return by_id.earnings()

    def find_all_earnings(
        self,
    ) -> dict[ProjectAllocationsId, Earnings]:
        return {cashflow.project_id(): cashflow.earnings() for cashflow in self.__cashflow_repository.find_all()}
