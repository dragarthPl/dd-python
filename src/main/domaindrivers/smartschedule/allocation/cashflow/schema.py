from domaindrivers.smartschedule.allocation.cashflow.cashflow import Cashflow
from domaindrivers.smartschedule.allocation.cashflow.cost import Cost
from domaindrivers.smartschedule.allocation.cashflow.income import Income
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.storage.uuid_pg import UUID
from sqlalchemy import BIGINT, Column, Table
from sqlalchemy.orm import composite, registry

mapper_registry = registry()

cashflows_table = Table(
    "cashflows",
    mapper_registry.metadata,
    Column("project_allocations_id", UUID(), primary_key=True),
    Column("cost", BIGINT(), nullable=False),
    Column("income", BIGINT(), nullable=False),
)


mapper_registry.map_imperatively(
    Cashflow,
    cashflows_table,
    column_prefix="_",
    properties={
        "_project_id": composite(
            ProjectAllocationsId,
            cashflows_table.c.project_allocations_id,
        ),
        "_cost_value": composite(
            Cost,
            cashflows_table.c.cost,
        ),
        "_income_value": composite(
            Income,
            cashflows_table.c.income,
        ),
    },
)
