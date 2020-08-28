__all__ = [
    "Logger",
]


class Logger:
    __slots__ = ()

    def log(self, message: str) -> None:
        raise NotImplementedError()
