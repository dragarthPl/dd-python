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
