from domaindrivers.smartschedule.resource.device.device import Device
from domaindrivers.smartschedule.resource.device.device_id import DeviceId
from domaindrivers.storage.uuid_pg import UUID
from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import composite, registry

mapper_registry = registry()

devices_table = Table(
    "devices",
    mapper_registry.metadata,
    Column("device_id", UUID(), primary_key=True),
    Column("version", Integer, nullable=False, default=0),
    Column("model", String, nullable=False),
    Column("capabilities", JSONB, nullable=True),
)

mapper_registry.map_imperatively(
    Device,
    devices_table,
    version_id_col=devices_table.c.version,
    column_prefix="_",
    properties={
        "_id": composite(
            DeviceId,
            devices_table.c.device_id,
        ),
    },
)
