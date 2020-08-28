from ioc_article.logger import (
    LoggerFactory,
)
from ioc_article.user_service import (
    UserServiceFactory,
)
from ..v2.Key import Key
from ..v2.service_locator import service_locator
from .ConsoleLoggerInitCommand import ConsoleLoggerInitCommand
from .UserServiceImplInitCommand import UserServiceImplInitCommand
from .use_factory import use_factory
from .call_init_commands import call_init_commands


__all__ = [
    "init",
]


def init() -> None:
    logger_factory, set_logger_factory = use_factory(Key(LoggerFactory), service_locator)
    user_service_factory, set_user_service_factory = use_factory(Key(UserServiceFactory), service_locator)
    call_init_commands([
        ConsoleLoggerInitCommand(
            set_logger_factory=set_logger_factory
        ),
        UserServiceImplInitCommand(
            logger_factory=logger_factory,
            set_user_service_factory=set_user_service_factory,
        ),
    ])
