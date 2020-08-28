from ioc_article.logger import (
    Logger,
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
        "__logger",
    )

    def __init__(self, logger: Logger) -> None:
        self.__logger = logger

    def create(self, email: str) -> User:
        self.__logger.log(f"Creating user with email '{email}'...")
        ...
