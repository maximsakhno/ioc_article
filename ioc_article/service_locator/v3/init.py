from ioc_article.logger import (
    LoggerFactory,
)
from ioc_article.user_service import (
    UserServiceFactory,
    UserServiceFactoryImpl,
)
from ..v2.Key import Key
from ..v2.service_locator import service_locator
from .UserServiceImpl import UserServiceImpl
from .get_factory_proxy import get_factory_proxy


__all__ = [
    "init",
]


def init() -> None:
    logger_factory_proxy = get_factory_proxy(Key(LoggerFactory), service_locator)
    user_service = UserServiceImpl(logger_factory_proxy)
    service_locator.set_factory(Key(UserServiceFactory), UserServiceFactoryImpl(user_service))
