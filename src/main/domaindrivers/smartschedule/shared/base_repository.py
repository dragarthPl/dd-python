from abc import ABC
from typing import Generic, Optional, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


# to use if we don't want to expose findAll() method from spring-data-jpa for entities with possible large number of records
class BaseRepository(ABC, Generic[T, ID]):
    def find_by_id(self, entity_id: ID) -> Optional[T]: ...

    def get_reference_by_id(self, entity_id: ID) -> T:
        pass

    def exists_by_id(self, entity_id: ID) -> bool:
        pass

    def delete_by_id(self, entity_id: ID) -> None:
        pass

    def delete(self, entity: T) -> None:
        pass

    def count(self) -> int:
        pass

    def save(self, entity: T) -> None:
        pass

    def find_all_by_id(self, ids: list[ID]) -> list[T]:
        pass

    def save_all(self, entities: list[T]) -> None:
        pass
