from ioc_article.logger import (
    Logger,
    ConsoleLogger,
)
from .LoggerFactory import LoggerFactory


__all__ = [
    "ConsoleLoggerFactory",
]


class ConsoleLoggerFactory(LoggerFactory):
    __slots__ = ()

    def __call__(self, name: str = "root") -> Logger:
        return ConsoleLogger(name)
