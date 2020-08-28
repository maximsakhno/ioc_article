from ioc_article.logger import (
    ConsoleLogger,
)
from ioc_article.user_service import (
    User,
    UserService,
)


__all__ = [
    "UserServiceImpl",
]


class UserServiceImpl(UserService):
    __slots__ = ()

    def create(self, email: str) -> User:
        logger = ConsoleLogger("user_service")
        logger.log(f"Creating user with email '{email}'...")
        ...
