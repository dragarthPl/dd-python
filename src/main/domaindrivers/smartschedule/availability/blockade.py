from attr import frozen
from domaindrivers.smartschedule.availability.owner import Owner


@frozen
class Blockade:
    taken_by: Owner
    disabled: bool

    @classmethod
    def none(cls) -> "Blockade":
        return cls(Owner.none(), False)

    @classmethod
    def disabled_by(cls, owner: Owner) -> "Blockade":
        return cls(owner, True)

    @classmethod
    def owned_by(cls, owner: Owner) -> "Blockade":
        return cls(owner, False)

    def can_be_taken_by(self, requester: Owner) -> bool:
        return bool(self.taken_by.by_none() or self.taken_by == requester)

    def is_disabled_by(self, owner: Owner) -> bool:
        return bool(self.disabled and owner == self.taken_by)
