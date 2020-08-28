from typing import (
    Callable,
)
from ioc_article.logger import (
    LoggerFactory,
)
from ioc_article.user_service import (
    UserServiceFactory,
    UserServiceFactoryImpl,
)
from .UserServiceImpl import UserServiceImpl
from .InitCommand import InitCommand


__all__ = [
    "UserServiceImplInitCommand",
]


class UserServiceImplInitCommand(InitCommand):
    __slots__ = (
        "__logger_factory",
        "__set_user_service_factory",
    )

    def __init__(
        self,
        logger_factory: LoggerFactory,
        set_user_service_factory: Callable[[UserServiceFactory], None],
    ) -> None:
        self.__logger_factory = logger_factory
        self.__set_user_service_factory = set_user_service_factory

    def __call__(self) -> None:
        user_service = UserServiceImpl(self.__logger_factory("user_service"))
        self.__set_user_service_factory(UserServiceFactoryImpl(user_service))
