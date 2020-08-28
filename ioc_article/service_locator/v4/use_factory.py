from typing import (
    TypeVar,
    Callable,
    Tuple,
)
from ..v2.Key import Key
from ..v2.ServiceLocator import ServiceLocator
from ..v3.get_factory_proxy import get_factory_proxy


__all__ = [
    "use_factory",
]


F = TypeVar("F", bound=Callable)


def use_factory(key: Key[F], service_locator: ServiceLocator) -> Tuple[F, Callable[[F], None]]:
    factory = get_factory_proxy(key, service_locator)

    def set_factory(__factory: F, /) -> None:
        service_locator.set_factory(key, __factory)

    return factory, set_factory
