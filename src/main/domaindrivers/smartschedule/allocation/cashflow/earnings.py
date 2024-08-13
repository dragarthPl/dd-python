import hashlib
from decimal import Decimal
from typing import Any

from attr import frozen


@frozen
class Earnings:
    earnings: Decimal

    @classmethod
    def of(cls, integer: int) -> "Earnings":
        return cls(Decimal(integer))

    def __eq__(self, other: Any) -> bool:
        if other is None or not isinstance(other, Earnings):
            return False
        return bool(self.earnings == other.earnings)

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.earnings).encode("utf-8"))

        return int(m.hexdigest(), 16)

    def to_decimal(self) -> Decimal:
        return self.earnings

    def greater_than(self, value: "Earnings") -> bool:
        return self.earnings > value.earnings
