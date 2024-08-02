from abc import ABC
from typing import Generic, TypeVar

from domaindrivers.utils.optional import Optional

Entity = TypeVar("Entity")
Id = TypeVar("Id")


class Repository(ABC, Generic[Entity, Id]):
    def get_by_id(self, entity_id: Id) -> Entity:
        pass

    def find_by_id(self, entity_id: Id) -> Optional[Entity] | None:
        pass

    def find_all_by_id(self, ids: list[Id]) -> list[Entity]:
        pass

    def save(self, entity: Entity) -> Entity | None:
        pass

    def delete(self, entity: Entity) -> None:
        pass
