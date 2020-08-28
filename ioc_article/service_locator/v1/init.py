from ioc_article.logger import (
    ConsoleLogger,
)
from .UserServiceImpl import UserServiceImpl
from .service_locator import service_locator


__all__ = [
    "init",
]


def init() -> None:

    def get_console_logger(name: str = "root") -> ConsoleLogger:
        return ConsoleLogger(name)

    service_locator.register("logger", get_console_logger)

    user_service = UserServiceImpl()
    service_locator.register("user_service", lambda: user_service)
