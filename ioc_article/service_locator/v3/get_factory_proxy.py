from typing import (
    TypeVar,
    Callable,
)
from ..v2.Key import Key
from ..v2.ServiceLocator import ServiceLocator


__all__ = [
    "get_factory_proxy",
]


F = TypeVar("F", bound=Callable)


def get_factory_proxy(key: Key[F], service_locator: ServiceLocator) -> F: ...
