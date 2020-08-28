import sys
from .Logger import Logger


__all__ = [
    "ConsoleLogger",
]


class ConsoleLogger(Logger):
    __slots__ = (
        "__name",
    )

    def __init__(self, name: str) -> None:
        self.__name = name

    def log(self, message: str) -> None:
        sys.stdout.write(f"{self.__name}: {message}\n")
