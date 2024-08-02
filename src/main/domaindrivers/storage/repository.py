from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from domaindrivers.utils.optional import Optional

Entity = TypeVar("Entity")
Id = TypeVar("Id")


class Repository(ABC, Generic[Entity, Id]):
    @abstractmethod
    def get_by_id(self, entity_id: Id) -> Entity:
        pass

    @abstractmethod
    def find_by_id(self, entity_id: Id) -> Optional[Entity] | None:
        pass

    @abstractmethod
    def find_all_by_id(self, ids: set[Id]) -> list[Entity]:
        pass

    @abstractmethod
    def save(self, entity: Entity) -> Entity | None:
        pass

    @abstractmethod
    def delete(self, entity: Entity) -> None:
        pass

    @abstractmethod
    def find_all(self) -> list[Entity]:
        pass
