import uuid
from uuid import UUID

from attr import frozen


@frozen
class Owner:
    owner: UUID

    @classmethod
    def none(cls) -> "Owner":
        return cls(None)

    @classmethod
    def new_one(cls) -> "Owner":
        return cls(uuid.uuid4())

    @classmethod
    def of(cls, owner: UUID) -> "Owner":
        return cls(owner)

    def by_none(self) -> bool:
        return self.none() == self

    def id(self) -> UUID:
        return self.owner
