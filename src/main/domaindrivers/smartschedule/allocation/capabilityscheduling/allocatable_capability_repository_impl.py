from typing import cast

import injector
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability import AllocatableCapability
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from domaindrivers.smartschedule.allocation.capabilityscheduling.allocatable_capability_repository import (
    AllocatableCapabilityRepository,
)
from domaindrivers.utils.optional import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session


class AllocatableCapabilityRepositoryImpl(AllocatableCapabilityRepository):  # type: ignore
    @injector.inject
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, project: AllocatableCapability) -> None:
        self.session.add(project)

    def save_all(self, entities: list[AllocatableCapability]) -> None:
        self.session.add_all(entities)

    def find_by_id(self, allocatable_capability_id: AllocatableCapabilityId) -> Optional[AllocatableCapability]:
        return Optional(
            self.session.query(AllocatableCapability)
            .filter_by(_allocatable_capability_id=allocatable_capability_id)
            .first()
        )

    def find_all_by_id(self, ids: list[AllocatableCapabilityId]) -> list[AllocatableCapability]:
        return cast(
            list[AllocatableCapability],
            self.session.query(AllocatableCapability)
            .where(
                or_(
                    *[
                        AllocatableCapability._allocatable_capability_id == allocatable_capability_id
                        for allocatable_capability_id in ids
                    ]
                )
            )
            .all(),
        )

    def find_all(self) -> list[AllocatableCapability]:
        return cast(list[AllocatableCapability], self.session.query(AllocatableCapability).all())

    def exists_by_id(self, allocatable_capability_id: AllocatableCapabilityId) -> bool:
        return cast(
            bool,
            self.session.query(AllocatableCapability).filter_by(_id=allocatable_capability_id.get_id()).count() > 0,
        )

    def delete(self, project: AllocatableCapability) -> None:
        self.session.delete(project)
        self.session.commit()
