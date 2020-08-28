from typing import (
    Callable,
)
from ioc_article.logger import (
    LoggerFactory,
    ConsoleLoggerFactory,
)
from .InitCommand import InitCommand


__all__ = [
    "ConsoleLoggerInitCommand",
]


class ConsoleLoggerInitCommand(InitCommand):
    __slots__ = (
        "__set_logger_factory",
    )

    def __init__(self, set_logger_factory: Callable[[LoggerFactory], None]) -> None:
        self.__set_logger_factory = set_logger_factory

    def __call__(self) -> None:
        self.__set_logger_factory(ConsoleLoggerFactory())
