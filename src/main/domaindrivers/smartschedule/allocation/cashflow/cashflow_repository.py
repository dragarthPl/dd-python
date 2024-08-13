from domaindrivers.smartschedule.allocation.cashflow.cashflow import Cashflow
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.storage.repository import Repository


class CashflowRepository(Repository[Cashflow, ProjectAllocationsId]):
    pass
