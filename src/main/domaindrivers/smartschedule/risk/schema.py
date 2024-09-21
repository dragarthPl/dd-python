from domaindrivers.smartschedule.allocation.cashflow.earnings import Earnings
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.risk.risk_periodic_check_saga import RiskPeriodicCheckSaga
from domaindrivers.smartschedule.risk.risk_periodic_check_saga_id import RiskPeriodicCheckSagaId
from domaindrivers.storage.uuid_pg import UUID
from sqlalchemy import BIGINT, Column, Integer, Table, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import composite, registry

mapper_registry = registry()

project_risk_sagas_table = Table(
    "project_risk_sagas",
    mapper_registry.metadata,
    Column("project_risk_saga_id", UUID(), primary_key=True),
    Column("project_allocations_id", UUID(), nullable=True),
    Column("earnings", BIGINT(), nullable=False),
    Column("missing_demands", JSONB, nullable=False),
    Column("deadline", TIMESTAMP(timezone=True), nullable=True),
    Column("version", Integer, nullable=False, default=0),
)

mapper_registry.map_imperatively(
    RiskPeriodicCheckSaga,
    project_risk_sagas_table,
    version_id_col=project_risk_sagas_table.c.version,
    column_prefix="_",
    properties={
        "_risk_saga_id": composite(
            RiskPeriodicCheckSagaId,
            project_risk_sagas_table.c.project_risk_saga_id,
        ),
        "_project_id": composite(
            ProjectAllocationsId,
            project_risk_sagas_table.c.project_allocations_id,
        ),
        "_earnings_value": composite(
            Earnings,
            project_risk_sagas_table.c.earnings,
        ),
    },
)
