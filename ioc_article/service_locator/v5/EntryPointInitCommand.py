from typing import (
    Sequence,
    List,
    Dict,
)
from pkg_resources import (
    EntryPoint,
    iter_entry_points,
)
from ..v4.InitCommand import InitCommand


__all__ = [
    "EntryPointInitCommand",
]


class EntryPointInitCommand(InitCommand):
    __slots__ = (
        "__group",
        "__init_command_names",
    )

    def __init__(self, group: str, init_command_names: Sequence[str]) -> None:
        self.__group = group
        self.__init_command_names = init_command_names

    def __call__(self) -> None:
        entry_point: EntryPoint
        init_commands: Dict[str, InitCommand] = {}
        for entry_point in iter_entry_points(self.__group):
            init_command_name = entry_point.name
            if init_command_name not in self.__init_command_names:
                continue

            init_command = entry_point.load()
            if not isinstance(init_command, InitCommand):
                raise TypeError(entry_point, InitCommand) from None

            init_commands[init_command_name] = init_command

        init_command_list: List[InitCommand] = []
        for init_command_name in self.__init_command_names:
            init_command = init_commands[init_command_name]
            init_command_list.append(init_command)

        for init_command in init_command_list:
            init_command()
