from domaindrivers.smartschedule.allocation.project_allocations import ProjectAllocations
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.storage.uuid_pg import UUID
from sqlalchemy import Column, Table, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import composite, registry

mapper_registry = registry()

projects_table = Table(
    "project_allocations",
    mapper_registry.metadata,
    Column("project_allocations_id", UUID(), primary_key=True),
    Column("allocations", JSONB, nullable=False),
    Column("demands", JSONB, nullable=True),
    Column("from_date", TIMESTAMP(timezone=True), nullable=True),
    Column("to_date", TIMESTAMP(timezone=True), nullable=True),
)

mapper_registry.map_imperatively(
    ProjectAllocations,
    projects_table,
    column_prefix="_",
    properties={
        "_project_id": composite(
            ProjectAllocationsId,
            projects_table.c.project_allocations_id,
        ),
        "_time_slot": composite(
            TimeSlot,
            projects_table.c.from_date,
            projects_table.c.to_date,
        ),
    },
)
