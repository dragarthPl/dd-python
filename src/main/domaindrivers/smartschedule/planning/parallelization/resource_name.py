import hashlib
from typing import Any

from attr import frozen


@frozen
class ResourceName:
    name: str

    def __eq__(self, other: Any) -> bool:
        if other is None or not isinstance(other, ResourceName):
            return False
        return bool(self.name == other.name)

    def __hash__(self) -> int:
        m = hashlib.md5()
        m.update(str(self.name).encode("utf-8"))

        return int(m.hexdigest(), 16)
