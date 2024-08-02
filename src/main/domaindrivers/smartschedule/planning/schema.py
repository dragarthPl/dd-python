from domaindrivers.smartschedule.planning.project import Project
from domaindrivers.smartschedule.planning.project_id import ProjectId
from domaindrivers.storage.uuid_pg import UUID
from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import composite, registry

mapper_registry = registry()

projects_table = Table(
    "projects",
    mapper_registry.metadata,
    Column("project_id", UUID(), primary_key=True),
    Column("version", Integer, nullable=False, default=0),
    Column("name", String, nullable=False),
    Column("parallelized_stages", JSONB, nullable=False),
    Column("demands_per_stage", JSONB, nullable=True),
    Column("all_demands", JSONB, nullable=True),
    Column("chosen_resources", JSONB, nullable=True),
    Column("schedule", JSONB, nullable=True),
)

mapper_registry.map_imperatively(
    Project,
    projects_table,
    version_id_col=projects_table.c.version,
    column_prefix="_",
    properties={
        "_id": composite(
            ProjectId,
            projects_table.c.project_id,
        ),
    },
)
