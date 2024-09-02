from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability import AllocatableCapability
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_resource_id import AllocatableResourceId
from domaindrivers.smartschedule.shared.time_slot.time_slot import TimeSlot
from domaindrivers.storage.uuid_pg import UUID
from sqlalchemy import Column, Table, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import composite, registry

mapper_registry = registry()

allocatable_capabilities_table = Table(
    "allocatable_capabilities",
    mapper_registry.metadata,
    Column("id", UUID(), primary_key=True),
    Column("resource_id", UUID(), nullable=False),
    Column("capability", JSONB, nullable=True),
    Column("from_date", TIMESTAMP(timezone=True), nullable=True),
    Column("to_date", TIMESTAMP(timezone=True), nullable=True),
)

mapper_registry.map_imperatively(
    AllocatableCapability,
    allocatable_capabilities_table,
    column_prefix="_",
    properties={
        "_allocatable_capability_id": composite(
            AllocatableCapabilityId,
            allocatable_capabilities_table.c.id,
        ),
        "_allocatable_resource_id": composite(
            AllocatableResourceId,
            allocatable_capabilities_table.c.resource_id,
        ),
        "_time_slot": composite(
            TimeSlot,
            allocatable_capabilities_table.c.from_date,
            allocatable_capabilities_table.c.to_date,
        ),
    },
)
