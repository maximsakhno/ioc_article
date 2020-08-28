from .UserService import UserService


__all__ = [
    "UserServiceFactory",
]


class UserServiceFactory:
    __slots__ = ()

    def __call__(self) -> UserService:
        raise NotImplementedError()
