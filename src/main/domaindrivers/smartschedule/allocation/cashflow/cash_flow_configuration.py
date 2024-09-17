from typing import cast, Type

import injector
from domaindrivers.smartschedule.allocation.cashflow.cash_flow_facade import CashFlowFacade
from domaindrivers.smartschedule.allocation.cashflow.cashflow_repository import CashflowRepository
from domaindrivers.smartschedule.allocation.cashflow.cashflow_repository_sqlalchemy import CashflowRepositorySqlalchemy
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher
from injector import Module, provider, singleton
from sqlalchemy.orm import Session


class CashFlowConfiguration(Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(cast(Type[CashflowRepository], CashflowRepository), to=CashflowRepositorySqlalchemy)

    @singleton
    @provider
    def cash_flow_facade(
        self, session: Session, cashflow_repository: CashflowRepository, events_publisher: EventsPublisher
    ) -> CashFlowFacade:
        return CashFlowFacade(session, cashflow_repository, events_publisher)
