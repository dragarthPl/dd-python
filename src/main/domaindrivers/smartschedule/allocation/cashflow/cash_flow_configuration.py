import injector
from domaindrivers.smartschedule.allocation.cashflow.cash_flow_facade import CashFlowFacade
from domaindrivers.smartschedule.allocation.cashflow.cashflow_repository import CashflowRepository
from domaindrivers.smartschedule.allocation.cashflow.cashflow_sqlalchemy_repository import CashflowSqlalchemyRepository
from domaindrivers.smartschedule.shared.events_publisher import EventsPublisher
from injector import Module, provider, singleton
from sqlalchemy.orm import Session


class CashFlowConfiguration(Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(CashflowRepository, to=CashflowSqlalchemyRepository)

    @singleton
    @provider
    def cash_flow_facade(
        self, session: Session, cashflow_repository: CashflowRepository, events_publisher: EventsPublisher
    ) -> CashFlowFacade:
        return CashFlowFacade(session, cashflow_repository, events_publisher)
