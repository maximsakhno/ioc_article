# Python-приложение: расширяем во всех местах. Часть 3

В предыдущих частях мы пришли к концепции команд инициализации приложения, которые сами по себе являются независимыми друг от друга, однако их можно связать с помощью локатора служб. В этой части рассмотрим, как мы будем применять это для решения поставленной задачи.

Для начала реализуем команду инициализации, которая будет загружать другие команды инициализации, используя механизм точек доступа в Python:

``` Python
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
```

Данная команда принимает в конструкторе название группы и список названий команд, которые нужно загрузить и выполнить. Команды будут выполнены в том порядке, в котором они указаны в списке. Список названий команд инициализации можно задать как константу, а можно получить его из других источников, например, из конфигурационного файла. Теперь для инициализации нам достаточно лишь одной этой команды. Код, который её вызывает, может быть таким:

``` Python
init_command = EntryPointInitCommand(
    group="init_commands",
    init_command_names=read_from_file("init_command_names.txt"),
)
```

Остальные команды нужно указать как точки входа:

``` Python
setup(
    ...
    entry_points={
        "init_commands": [
            "console_logger = project.console_logger:init_command",
            "file_logger = project.file_logger:init_command",
            "user_serivce_impl = project.user_service.impl:init_command",
        ],
    },
    ...
)
```

Например, так может выглядеть содержимое модуля `project.console_logger`, откуда будет загружиться `ConsoleLoggerInitCommand`:

``` Python
_, set_logger_factory = use_factory(Key(LoggerFactory))
init_command = ConsoleLoggerInitCommand(set_logger_factory)
```

Аналогично будут выглядеть и осталные модули.

Содержимое файла `init_command_names.txt`:

``` Text
console_logger
user_service_impl
```

Возвращаясь к исходной задаче: теперь у клиента в зависимости от его требований мы можем просто перечислить нужные нам команды инициализации в конфигурационном файле и таким образом заменить или добавить люобой необходимый компонент приложения. Например, если новому клиенту нужно логгировать в файл, а не консоль, то достаточно заменить одну строчку в конфигурационном файле его приложения. В случае, если клиенту требуется логгировать не в консоль и не в файл, а в базу данных, и по тем или иным причинам мы не можем добавить новый логгер в кодовую базу проекта, то нам достаточно создать отдельный проект с этим логгером, установить его вместе с основным проектом у клиента и в конфигурационном файле в качестве логгера указать его.

Модуль `setup.py` проекта с новым логгером:

``` Python
setup(
    ...
    entry_points={
        "init_commands": [
            "database_logger = database_logger:init_command",
        ],
    },
    ...
)
```

Содержимое файла `init_command_names.txt` у этого клиента:

``` Text
database_logger
user_service_impl
```

В этой, завершающей, части мы продемонстрировали, как можно использовать наше решение для того, чтобы заменять существующие и добавлять новые компоненты, просто дописывая новый код и меняя конфигурационные файлы у клиентов.

А вам приходилось решать задачу разных конфигураций для одного и того же приложения? Если да, то как подходили к решению такой проблемы?
