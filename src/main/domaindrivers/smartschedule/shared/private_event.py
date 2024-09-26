from abc import ABC, abstractmethod
from datetime import datetime


# metadata:
# correlationId
# potential aggregate's id
# causationId - id of a message that caused this message
# messageId - unique id of the
# user - if there is any (might be a system event)
class PrivateEvent(ABC):
    @abstractmethod
    def occurred_at(self) -> datetime: ...
