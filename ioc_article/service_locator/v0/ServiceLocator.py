from typing import (
    Any,
    Dict,
)
from .DependencyResolutionException import DependencyResolutionException


__all__ = [
    "ServiceLocator",
]


class ServiceLocator:
    __slots__ = (
        "__instances",
    )

    def __init__(self) -> None:
        self.__instances: Dict[str, Any] = {}

    def register(self, key: str, instance: Any) -> None:
        self.__instances[key] = instance

    def resolve(self, key: str) -> Any:
        try:
            return self.__instances[key]
        except KeyError:
            raise DependencyResolutionException(key) from None
