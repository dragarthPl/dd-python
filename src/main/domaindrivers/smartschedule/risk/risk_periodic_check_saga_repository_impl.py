from typing import cast

import injector
from domaindrivers.smartschedule.risk.risk_periodic_check_saga import RiskPeriodicCheckSaga
from domaindrivers.smartschedule.risk.risk_periodic_check_saga_id import RiskPeriodicCheckSagaId
from domaindrivers.smartschedule.risk.risk_periodic_check_saga_repository import RiskPeriodicCheckSagaRepository
from domaindrivers.utils.optional import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session


class RiskPeriodicCheckSagaRepositoryImpl(RiskPeriodicCheckSagaRepository):  # type: ignore
    @injector.inject
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, risk_periodic_check_saga: RiskPeriodicCheckSaga) -> None:
        self.session.add(risk_periodic_check_saga)

    def find_by_id(self, risk_saga_id: RiskPeriodicCheckSagaId) -> Optional[RiskPeriodicCheckSaga]:
        return Optional(self.session.query(RiskPeriodicCheckSaga).filter_by(_risk_saga_id=risk_saga_id.id()).first())

    def find_by_project_id(self, project_id: str) -> RiskPeriodicCheckSaga:
        return self.session.query(RiskPeriodicCheckSaga).filter_by(_project_id=project_id).first()

    def find_by_project_id_in(self, interested: list[str]) -> list[RiskPeriodicCheckSaga]:
        return cast(
            list[RiskPeriodicCheckSaga],
            self.session.query(RiskPeriodicCheckSaga)
            .where(or_(*[RiskPeriodicCheckSaga._project_id == project_id for project_id in interested]))
            .all(),
        )

    def find_all_by_id(self, ids: list[RiskPeriodicCheckSagaId]) -> list[RiskPeriodicCheckSaga]:
        return cast(
            list[RiskPeriodicCheckSaga],
            self.session.query(RiskPeriodicCheckSaga)
            .where(or_(*[RiskPeriodicCheckSaga._risk_saga_id == risk_saga_id for risk_saga_id in ids]))
            .all(),
        )

    def find_all(self) -> list[RiskPeriodicCheckSaga]:
        return cast(list[RiskPeriodicCheckSaga], self.session.query(RiskPeriodicCheckSaga).all())

    def delete(self, risk_periodic_check_saga: RiskPeriodicCheckSaga) -> None:
        self.session.delete(risk_periodic_check_saga)
        self.session.commit()
