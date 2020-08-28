from typing import (
    TypeVar,
    Any,
    Callable,
    Dict,
)
from .FactoryNotFoundByKeyException import FactoryNotFoundByKeyException
from .Key import Key


__all__ = [
    "ServiceLocator",
]


F = TypeVar("F", bound=Callable)


class ServiceLocator:
    __slots__ = (
        "__factories",
    )

    def __init__(self) -> None:
        self.__factories: Dict[Key[Any], Any] = {}

    def set_factory(self, key: Key[F], factory: F) -> None:
        self.__factories[key] = factory

    def get_factory(self, key: Key[F]) -> F:
        try:
            return self.__factories[key]
        except KeyError:
            raise FactoryNotFoundByKeyException(key) from None
