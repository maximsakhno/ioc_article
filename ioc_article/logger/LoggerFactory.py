from ioc_article.logger import (
    Logger,
)


__all__ = [
    "LoggerFactory",
]


class LoggerFactory:
    __slots__ = ()

    def __call__(self, name: str = "root") -> Logger:
        raise NotImplementedError()
