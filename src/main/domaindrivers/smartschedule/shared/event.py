from datetime import datetime
from typing import Protocol


class Event(Protocol):
    def occurred_at(self) -> datetime: ...
