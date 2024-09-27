from typing import cast

import injector
from domaindrivers.smartschedule.allocation.cashflow.cashflow import Cashflow
from domaindrivers.smartschedule.allocation.cashflow.cashflow_repository import CashflowRepository
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.storage.repository import Repository
from domaindrivers.utils.optional import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session


class CashflowSqlalchemyRepository(CashflowRepository, Repository[Cashflow, ProjectAllocationsId]):  # type: ignore
    @injector.inject
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, cashflow: Cashflow) -> None:
        self.session.add(cashflow)
        self.session.commit()

    def find_by_id(self, project_id: ProjectAllocationsId) -> Optional[Cashflow]:
        return Optional(self.session.query(Cashflow).filter_by(_project_allocations_id=project_id.id()).first())

    def find_all_by_id(self, ids: list[ProjectAllocationsId]) -> list[Cashflow]:
        return cast(
            list[Cashflow],
            self.session.query(Cashflow).where(or_(*[Cashflow._project_id == project_id for project_id in ids])).all(),
        )

    def find_all(self) -> list[Cashflow]:
        return cast(list[Cashflow], self.session.query(Cashflow).all())

    def delete(self, cashflow: Cashflow) -> None:
        self.session.delete(cashflow)
        self.session.commit()
