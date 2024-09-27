from typing import Final
from unittest.mock import MagicMock

from domaindrivers.smartschedule.allocation.cashflow.cash_flow_facade import CashFlowFacade
from domaindrivers.smartschedule.allocation.cashflow.cashflow import Cashflow
from domaindrivers.smartschedule.allocation.cashflow.cashflow_repository import CashflowRepository
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher
from domaindrivers.utils.optional import Optional


class InMemoryCashflowRepository(CashflowRepository):
    __cashflows: Final[dict[ProjectAllocationsId, Cashflow]]

    def __init__(self) -> None:
        self.__cashflows = {}

    def save(self, cashflow: Cashflow) -> Cashflow:
        self.__cashflows[cashflow._project_id] = cashflow
        return self.__cashflows[cashflow._project_id]

    def find_all(self) -> list[Cashflow]:
        return list(self.__cashflows.values())

    def find_by_id(self, project_id: ProjectAllocationsId) -> Optional[Cashflow]:
        return Optional.of_nullable(self.__cashflows.get(project_id, None))


class CashFlowTestConfiguration:
    @staticmethod
    def cash_flow_facade(events_publisher: EventsPublisher) -> CashFlowFacade:
        return CashFlowFacade(MagicMock(), InMemoryCashflowRepository(), events_publisher)
