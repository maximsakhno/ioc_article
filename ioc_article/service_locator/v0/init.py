from ioc_article.logger import (
    ConsoleLogger,
)
from .UserServiceImpl import UserServiceImpl
from .service_locator import service_locator


__all__ = [
    "init",
]


def init() -> None:
    service_locator.register("logger", ConsoleLogger("root"))
    service_locator.register("user_service", UserServiceImpl())
