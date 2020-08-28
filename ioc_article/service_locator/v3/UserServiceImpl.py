from ioc_article.logger import (
    LoggerFactory,
)
from ioc_article.user_service import (
    User,
    UserService,
)


__all__ = [
    "UserServiceImpl",
]


class UserServiceImpl(UserService):
    __slots__ = (
        "__logger_factory",
    )

    def __init__(self, logger_factory: LoggerFactory) -> None:
        self.__logger_factory = logger_factory

    def create(self, email: str) -> User:
        logger = self.__logger_factory("user_service")
        logger.log(f"Creating user with email '{email}'...")
        ...
