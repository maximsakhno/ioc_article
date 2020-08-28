__all__ = [
    "InitCommand",
]


class InitCommand:
    __slots__ = ()

    def __call__(self) -> None:
        raise NotImplementedError()
