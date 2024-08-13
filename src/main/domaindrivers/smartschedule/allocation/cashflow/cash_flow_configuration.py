import injector
from domaindrivers.smartschedule.allocation.cashflow.cash_flow_facade import CashFlowFacade
from domaindrivers.smartschedule.allocation.cashflow.cashflow_repository import CashflowRepository
from domaindrivers.smartschedule.allocation.cashflow.cashflow_repository_impl import CashflowRepositoryImpl
from injector import Module, provider, singleton
from sqlalchemy.orm import Session


class CashFlowConfiguration(Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(CashflowRepository, to=CashflowRepositoryImpl)

    @singleton
    @provider
    def cash_flow_facade(self, session: Session, cashflow_repository: CashflowRepository) -> CashFlowFacade:
        return CashFlowFacade(session, cashflow_repository)
