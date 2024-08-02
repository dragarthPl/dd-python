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
