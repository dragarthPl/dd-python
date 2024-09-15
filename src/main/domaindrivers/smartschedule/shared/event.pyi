from abc import ABC, abstractmethod
from datetime import datetime

class Event(ABC):
    @abstractmethod
    def occurred_at(self) -> datetime: ...
