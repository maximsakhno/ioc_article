from typing import (
    TypeVar,
    Generic,
    Callable,
    Type,
)


__all__ = [
    "Key",
]


F = TypeVar("F", bound=Callable)


class Key(Generic[F]):
    __slots__ = ()

    def __init__(self, factory_type: Type[F], id: str = "") -> None: ...
