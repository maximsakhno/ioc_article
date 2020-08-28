from typing import (
    TypeVar,
    Any,
    Callable,
    Type,
)


__all__ = [
    "generate_singleton_factory",
]


F = TypeVar("F", bound=Callable)


def generate_singleton_factory(factory_type: Type[F], instance: Any) -> F: ...
