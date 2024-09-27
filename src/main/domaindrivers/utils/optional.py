from typing import Callable, Generic
from typing import Optional as TypingOptional
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


class Optional(Generic[T]):
    def __init__(self, value: TypingOptional[T] = None):
        self._value = value

    @staticmethod
    def empty() -> "Optional[T]":
        return Optional(None)

    @staticmethod
    def of(value: TypingOptional[T] = None) -> "Optional[T]":
        return Optional(value)

    def get(self) -> T:
        if self._value is None:
            raise ValueError("Value in optional was not present!")
        return self._value

    def or_else_throw(self) -> T:
        if self._value is None:
            raise ValueError("Value in optional was not present!")
        return self._value

    def map(self, select: Callable[[T], R]) -> "Optional[R]":
        if self._value is not None:
            return Optional.of(select(self._value))
        return Optional.empty()

    def is_present(self) -> bool:
        return self._value is not None

    def or_else_get(self, supplier: Callable[[], T]) -> T:
        if self._value is None:
            return supplier()
        return self._value

    def or_else(self, other: T) -> T:
        return self._value if self._value else other

    def if_present(self, consumer: Callable[[T], None]) -> None:
        if self._value is not None:
            consumer(self._value)

    def is_empty(self) -> bool:
        return self._value is None

    @classmethod
    def of_nullable(cls, value: T) -> "Optional[T]":
        return cls(value)
