from ioc_article.logger import (
    LoggerFactory,
)
from ioc_article.user_service import (
    User,
    UserService,
)
from .Key import Key
from .service_locator import service_locator


__all__ = [
    "UserServiceImpl",
]


class UserServiceImpl(UserService):
    __slots__ = ()

    def create(self, email: str) -> User:
        logger = service_locator.get_factory(Key(LoggerFactory))("user_service")
        logger.log(f"Creating user with email '{email}'...")
        ...
