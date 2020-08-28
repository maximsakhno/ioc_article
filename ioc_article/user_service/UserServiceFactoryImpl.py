from .UserService import UserService
from .UserServiceFactory import UserServiceFactory


__all__ = [
    "UserServiceFactoryImpl",
]


class UserServiceFactoryImpl(UserServiceFactory):
    __slots__ = (
        "__user_service",
    )

    def __init__(self, user_service: UserService) -> None:
        self.__user_service = user_service

    def __call__(self) -> UserService:
        return self.__user_service
