import hashlib
import uuid
from typing import Any

from attr import field, frozen
from domaindrivers.utils.serializable import Serializable


@frozen
class RiskPeriodicCheckSagaId(Serializable):
    __project_risk_saga_id: uuid.UUID = field(default=None)

    @classmethod
    def new_one(cls) -> "RiskPeriodicCheckSagaId":
        return cls(uuid.uuid4())

    def id(self) -> uuid.UUID:
        return self.__project_risk_saga_id

    def __composite_values__(self) -> tuple[uuid.UUID]:
        return (self.__project_risk_saga_id,)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, RiskPeriodicCheckSagaId):
            return False
        return self.__project_risk_saga_id == other.__project_risk_saga_id

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.__project_risk_saga_id).encode("utf-8"))

        return int(m.hexdigest(), 16)
