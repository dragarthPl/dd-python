from abc import ABC, abstractmethod

from domaindrivers.smartschedule.allocation.cashflow.cashflow import Cashflow
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.utils.optional import Optional


class CashflowRepository(ABC):
    @abstractmethod
    def find_by_id(self, project_id: ProjectAllocationsId) -> Optional[Cashflow]: ...

    @abstractmethod
    def save(self, cashflow: Cashflow) -> Cashflow: ...

    @abstractmethod
    def find_all(self) -> list[Cashflow]: ...
