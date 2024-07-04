import hashlib

from attr import frozen
from domaindrivers.smartschedule.optimization.total_weight import TotalWeight


@frozen
class Item:
    name: str
    value: float
    total_weight: TotalWeight

    def is_weight_zero(self) -> bool:
        return len(self.total_weight.components) == 0

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.name).encode("utf-8"))
        m.update(str(self.value).encode("utf-8"))
        m.update(str(self.total_weight).encode("utf-8"))

        return int(m.hexdigest(), 16)
