from ioc_article.logger import (
    Logger,
    LoggerFactory,
)
from ..v2.Key import Key
from ..v2.ServiceLocator import ServiceLocator


__all__ = [
    "LoggerFactoryProxy",
]


class LoggerFactoryProxy(LoggerFactory):
    __slots__ = (
        "__service_locator",
        "__key",
    )

    def __init__(self, service_locator: ServiceLocator, key: Key[LoggerFactory]) -> None:
        self.__service_locator = service_locator
        self.__key = key

    def __call__(self, name: str = "root") -> Logger:
        return self.__service_locator.get_factory(self.__key)(name)
