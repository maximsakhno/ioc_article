from .User import User


__all__ = [
    "UserService",
]


class UserService:
    __slots__ = ()

    def create(self, email: str) -> User:
        raise NotImplementedError()
