from ioc_article.logger import (
    Logger,
    LoggerFactory,
    ConsoleLogger,
)
from ioc_article.user_service import (
    UserServiceFactory,
)
from .UserServiceImpl import UserServiceImpl
from .Key import Key
from .generate_singleton_factory import generate_singleton_factory
from .generate_function_factory import generate_function_factory
from .service_locator import service_locator


__all__ = [
    "init",
]


def init() -> None:

    def get_console_logger(name: str = "root") -> Logger:
        return ConsoleLogger(name)

    logger_factory = generate_function_factory(LoggerFactory, get_console_logger)
    service_locator.set_factory(Key(LoggerFactory), logger_factory)

    user_service_factory = generate_singleton_factory(UserServiceFactory, UserServiceImpl())
    service_locator.register(Key(UserServiceFactory), user_service_factory)
