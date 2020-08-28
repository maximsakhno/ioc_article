from ioc_article.user_service import (
    User,
    UserService,
)
from .service_locator import service_locator


__all__ = [
    "UserServiceImpl",
]


class UserServiceImpl(UserService):
    __slots__ = ()

    def create(self, email: str) -> User:
        logger = service_locator.resolve("logger")
        logger.log(f"Creating user with email '{email}'...")
        ...
