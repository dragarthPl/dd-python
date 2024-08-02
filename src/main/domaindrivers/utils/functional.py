from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")
R = TypeVar("R")
U = TypeVar("U")
V = TypeVar("V")


def require_non_none(obj: Any) -> Any:
    if obj is None:
        raise AttributeError()
    return obj


class Predicate(Generic[T]):
    predicate_function: Callable[[T], bool]

    def __init__(self, predicate_function: Callable[[T], bool] | None = None):
        self.predicate_function = predicate_function

    def __call__(self, t: T) -> bool:
        return self.predicate_function(t)

    def test(self, t: T) -> bool:
        require_non_none(self.predicate_function)
        return self.predicate_function(t)

    def and_(self, other: Predicate[T]) -> Predicate[T]:
        require_non_none(other)
        return Predicate[T](lambda t: self.test(t) and other.test(t))

    def negate(self) -> Predicate[T]:
        return Predicate[T](lambda t: not self.test(t))

    def or_(self, other: Predicate[T]) -> Predicate[T]:
        require_non_none(other)
        return Predicate[T](lambda t: self.test(t) or other.test(t))

    def is_equal(self, target_ref: Any) -> Predicate[T]:
        return Predicate[T](lambda obj: bool(obj is None if not target_ref else lambda obj: target_ref == obj))

    def not_(self, target: Predicate[T]) -> Predicate[T]:
        require_non_none(target)
        return target.negate()


class Function(Generic[T, R]):
    function: Callable[[T], R]

    def __init__(self, function: Callable[[T], R] = lambda: None):
        self.function = function

    def __call__(self, t: T) -> R:
        return self.function(t)

    def apply(self, t: T) -> R:
        require_non_none(self.function)
        return self.function(t)

    def compose(self, before: Function[V, T]) -> Function[V, R]:
        require_non_none(before)
        return Function[V, R](lambda v: self.apply(before.apply(v)))

    def and_then(self, after: Function[R, V]) -> Function[T, V]:
        require_non_none(after)
        return Function[T, V](lambda t: after.apply(self.apply(t)))

    def identity(self) -> Function[T, T]:
        return Function[T, T](lambda t: t)


class BiFunction(Generic[T, U, R]):
    bi_function: Callable[[T, U], R]

    def __init__(self, bi_function: Callable[[T, U], R] = None):
        self.bi_function = bi_function

    def __call__(self, t: T, u: U) -> R:
        return self.bi_function(t, u)

    def apply(self, t: T, u: U) -> R:
        require_non_none(self.bi_function)
        return self.bi_function(t, u)

    def and_then(self, after: Function[R, V]) -> BiFunction[T, U, V]:
        require_non_none(after)
        return BiFunction[T, U, V](lambda t, u: after.apply(self.apply(t, u)))


if __name__ == "__main__":
    assert Predicate[str](lambda _: False).test("abc") is False
    assert BiFunction[int, int, int](lambda a, b: a + b).apply(3, 3) == 6
