from typing import (
    Sequence,
)
from .InitCommand import InitCommand


__all__ = [
    "call_init_commands",
]


def call_init_commands(init_commands: Sequence[InitCommand]) -> None: ...
