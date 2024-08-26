from domaindrivers.smartschedule.allocation.project_allocations import ProjectAllocations
from domaindrivers.smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.storage.uuid_pg import UUID
from sqlalchemy import Column, Table, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import composite, registry

mapper_registry = registry()

project_allocations_table = Table(
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
    project_allocations_table,
    column_prefix="_",
    properties={
        "_project_id": composite(
            ProjectAllocationsId,
            project_allocations_table.c.project_allocations_id,
        ),
        "_time_slot": composite(
            TimeSlot,
            project_allocations_table.c.from_date,
            project_allocations_table.c.to_date,
        ),
    },
)
