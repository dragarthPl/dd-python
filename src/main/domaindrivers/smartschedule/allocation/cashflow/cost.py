import hashlib
from decimal import Decimal
from typing import Any

from attr import field, frozen


@frozen
class Cost:
    cost: Decimal = field(default=None)

    def __composite_values__(self) -> tuple[Decimal]:
        return (self.cost,)

    @classmethod
    def of(cls, integer: int) -> "Cost":
        return cls(Decimal(integer))

    def __eq__(self, other: Any) -> bool:
        if other is None or not isinstance(other, Cost):
            return False
        return bool(self.cost == other.cost)

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.cost).encode("utf-8"))

        return int(m.hexdigest(), 16)

    def value(self) -> Decimal:
        return self.cost
