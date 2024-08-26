from domaindrivers.smartschedule.resource.employees.employee import Employee
from domaindrivers.smartschedule.resource.employees.employee_id import EmployeeId
from domaindrivers.smartschedule.resource.employees.seniority import Seniority
from domaindrivers.storage.uuid_pg import UUID
from sqlalchemy import Column, Enum, Integer, String, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import composite, registry

mapper_registry = registry()

employees_table = Table(
    "employees",
    mapper_registry.metadata,
    Column("employee_id", UUID(), primary_key=True),
    Column("version", Integer, nullable=False, default=0),
    Column("name", String, nullable=False),
    Column("seniority", Enum(Seniority), nullable=False),
    Column("last_name", String, nullable=False),
    Column("capabilities", JSONB, nullable=True),
)

mapper_registry.map_imperatively(
    Employee,
    employees_table,
    version_id_col=employees_table.c.version,
    column_prefix="_",
    properties={
        "_id": composite(
            EmployeeId,
            employees_table.c.employee_id,
        ),
    },
)
