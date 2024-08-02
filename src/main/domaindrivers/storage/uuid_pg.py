import uuid
from typing import Any

from sqlalchemy import CHAR, Dialect, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class UUID(TypeDecorator):  # type: ignore
    impl = CHAR

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID())
        else:
            return self.impl

    def process_bind_param(self, value: Any, dialect: Dialect) -> Any:
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        if not isinstance(value, uuid.UUID):
            raise ValueError("Value must be a UUID instance")
        return str(value)

    def process_result_value(self, value: Any, dialect: Dialect) -> Any:
        if value is None:
            return value
        if isinstance(value, str):
            return uuid.UUID(value)
        return value
