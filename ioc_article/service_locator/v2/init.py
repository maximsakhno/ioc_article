from ioc_article.logger import (
    LoggerFactory,
    ConsoleLoggerFactory,
)
from ioc_article.user_service import (
    UserServiceFactory,
    UserServiceFactoryImpl,
)
from .UserServiceImpl import UserServiceImpl
from .Key import Key
from .service_locator import service_locator


__all__ = [
    "init",
]


def init() -> None:
    service_locator.set_factory(Key(LoggerFactory), ConsoleLoggerFactory())
    service_locator.set_factory(Key(UserServiceFactory), UserServiceFactoryImpl(UserServiceImpl()))
