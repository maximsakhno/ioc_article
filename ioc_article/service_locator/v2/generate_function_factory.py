from typing import (
    TypeVar,
    Any,
    Callable,
    Type,
)


__all__ = [
    "generate_function_factory",
]


F = TypeVar("F", bound=Callable)


def generate_function_factory(factory_type: Type[F], function: Callable[..., Any]) -> F: ...
