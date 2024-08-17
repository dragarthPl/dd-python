import uuid
from uuid import UUID

from attr import frozen


@frozen
class Owner:
    owner: UUID

    @classmethod
    def none(cls) -> "Owner":
        return Owner(None)

    @classmethod
    def new_one(cls) -> "Owner":
        return Owner(uuid.uuid4())

    def by_none(self) -> bool:
        return self.none() == self

    def id(self) -> UUID:
        return self.owner
