from typing import (
    Any,
    Callable,
    Dict,
)
from .DependencyResolutionException import DependencyResolutionException


__all__ = [
    "ServiceLocator",
]


class ServiceLocator:
    __slots__ = (
        "__factories",
    )

    def __init__(self) -> None:
        self.__factories: Dict[str, Callable[..., Any]] = {}

    def register(self, key: str, factory: Callable[..., Any]) -> None:
        self.__factories[key] = factory

    def resolve(self, __key: str, /, *args: Any, **kwargs: Any) -> Any:
        try:
            factory = self.__factories[__key]
        except KeyError:
            raise DependencyResolutionException(__key) from None

        return factory(*args, **kwargs)
