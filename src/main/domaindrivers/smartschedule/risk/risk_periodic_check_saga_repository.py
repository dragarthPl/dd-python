from abc import abstractmethod

from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.risk.risk_periodic_check_saga import RiskPeriodicCheckSaga
from domaindrivers.smartschedule.risk.risk_periodic_check_saga_id import RiskPeriodicCheckSagaId
from domaindrivers.storage.repository import Repository


class RiskPeriodicCheckSagaRepository(Repository[RiskPeriodicCheckSaga, RiskPeriodicCheckSagaId]):
    @abstractmethod
    def find_by_project_id(self, project_id: ProjectAllocationsId) -> RiskPeriodicCheckSaga: ...

    @abstractmethod
    def find_by_project_id_in(self, interested: list[ProjectAllocationsId]) -> list[RiskPeriodicCheckSaga]: ...

    def find_by_project_id_or_create(self, project_id: ProjectAllocationsId) -> RiskPeriodicCheckSaga:
        found: RiskPeriodicCheckSaga = self.find_by_project_id(project_id)
        if not found:
            found = self.save(RiskPeriodicCheckSaga(project_id=project_id))
        return found

    def find_by_project_id_in_or_else_create(
        self, interested: list[ProjectAllocationsId]
    ) -> list[RiskPeriodicCheckSaga]:
        found: list[RiskPeriodicCheckSaga] = self.find_by_project_id_in(interested)
        found_ids: list[ProjectAllocationsId] = list(map(lambda risk: risk.project_id(), found))
        missing: list[RiskPeriodicCheckSaga] = list(
            map(
                lambda project_id: RiskPeriodicCheckSaga(project_id=project_id),
                filter(lambda project_id: project_id not in found_ids, interested),
            )
        )
        missing = self.save_all(missing)
        return found + missing

    def save_all(self, risk_periodic_check_sagas: list[RiskPeriodicCheckSaga]) -> list[RiskPeriodicCheckSaga]: ...
