# Python-приложение: расширяем во всех местах. Часть 2

В певой части мы обозначили проблему и начали использовать для ее решения локатор служб. Несмотря на то, что он справляется с поставленной задачей, он всё же обладает рядом недостатков, часть из которых мы уже исправили в предыдущей части. Продолжим и дальше его улучшать.

Ранее мы не затрагивали главную проблему, а именно о том, что зависимости не объявляются явным образом в параметрах конструктора или метода, а скрыты в их реализациях. Даже прочитав их реализации нельзя определить полный список всех зависмостей того или иного компонента, потому что они могут быть скрыты внутри вложенных вызовов. Давайте объявим зависимости явным образом:

``` Python 
class UserServiceImpl(UserService):
    __slots__ = (
        "__logger_factory",
    )

    def __init__(self, logger_factory: LoggerFactory) -> None:
        self.__logger_factory = logger_factory

    def create(self, email: str) -> User:
        logger = self.__logger_factory("user_service")
        logger.log(f"Creating user with email '{email}'...")
        ...
```

Однако в тот момент, когда нам может потребоваться фабрика, она может быть еще не зарегистрирована в локаторе служб. Для ее решения будем генерировать прокси-фабрики:

``` Python
def get_proxy_factory(key: Key[F]) -> F: ...
```

Функция генерации прокси-фабрики получает на вход ключ, который содержит в себе интерфейс нужной нам фабрики, и возвращает экземпляр такой фабрики. При вызове прокси-фабрика как функции она будет пытаться получить фабрику, которая зарегистрирована по этому ключу в локаторе служб, и возвращать результат вызова этой фабрики с переданными параметрами. Приведем пример прокси-фабрики, которая будет сгенерирована функцией `get_proxy_factory` по ключу типа `Key[LoggerFactory]`:

``` Python
class LoggerProxyFactory(LoggerFactory):
    __slots__ = (
        "__key",
    )

    def __init__(self, key: Key[LoggerFactory]) -> None:
        self.__key = key

    def __call__(self, name: str = "root") -> Logger:
        factory = service_locator.get_factory(self.__key)
        return factory(name)
```

Это позволит получить нам экземпляр фабрики типа `LoggerFactory` в тот момент, когда она еще не зарегистрирована в локаторе служб, и связать наши компоненты при инициализации приложения. Теперь, когда нам доступны прокси-фабрики, перепишем нашу функцию инициализации, используя их:

``` Python
def init() -> None:
    logger_proxy_factory = get_proxy_factory(Key(LoggerFactory))
    user_service = UserServiceImpl(logger_proxy_factory)
    service_locator.set_factory(Key(UserServiceFactory), UserServiceFactoryImpl(user_service))
```

Однако нет никакой гарантии, что после инициализации приложения экземпляр класса `LoggerFactory`, от которого зависит `UserServiceImpl`, будет зарегистрирован. О таких вещах лучше узнавать если не на этапе статического анализа, то хотя бы во время инициализации приложения. Да и классу `UserServiceImpl` требуется не `LoggerFactory`, а непосредственно `Logger`. Таким образом, мы приходим к тому, что внедрение зависимости должно происходить на один уровень выше, а именно - в командах инициализации. Опишем интерфейс такой команды:

``` Python
class InitCommand:
    __slots__ = ()

    def __call__(self) -> None:
        raise NotImplementedError()
```

Реализация такой команды, регистрирующая `LoggerFactory`:

``` Python
class ConsoleLoggerInitCommand(InitCommand):
    __slots__ = (
        "__set_logger_factory",
    )

    def __init__(self, set_logger_factory: Callable[[LoggerFactory], None]) -> None:
        self.__set_logger_factory = set_logger_factory

    def __call__(self) -> None:
        self.__set_logger_factory(ConsoleLoggerFactory())
```

Обратите внимание, что тот факт, что эта команда регистрирует `LoggerFactory`, указан явным образом в конструкторе этой команды, но подробнее на этом остановимся позже.

Ниже представлена команда, регистрирующая `UserServiceFactory`.

```
class UserServiceImplInitCommand(InitCommand):
    __slots__ = (
        "__logger_factory",
        "__set_user_service_factory",
    )

    def __init__(
        self,
        logger_factory: LoggerFactory,
        set_user_service_factory: Callable[[UserServiceFactory], None],
    ) -> None:
        self.__logger_factory = logger_factory
        self.__set_user_service_factory = set_user_service_factory

    def __call__(self) -> None:
        user_service = UserServiceImpl(self.__logger_factory("user_service"))
        self.__set_user_service_factory(UserServiceFactoryImpl(user_service))
```

И в ней явным образом указано, что она зависит от `LoggerFactory`.

При этом `UserServiceImpl` зависит уже не от `LoggerFactory`, а непосредственно от `Logger`, что и дает нам гарантию того, что после инициализации приложения необходимые зависимости будут зарегистрированы, а в противном случае мы получим ошибку на этапе инициализации приложения.

``` Python
class UserServiceImpl(UserService):
    __slots__ = (
        "__logger",
    )

    def __init__(self, logger: Logger) -> None:
        self.__logger = logger

    def create(self, email: str) -> User:
        self.__logger.log(f"Creating user with email '{email}'...")
        ...
```

Инициализация приложения может выглядеть следующим образом:

``` Python 
def init() -> None:
    logger_proxy_factory, set_logger_factory = use_factory(Key(LoggerFactory))
    user_service_proxy_factory, set_user_service_factory = use_factory(Key(UserServiceFactory))
    call_init_commands([
        ConsoleLoggerInitCommand(
            set_logger_factory=set_logger_factory
        ),
        UserServiceImplInitCommand(
            logger_factory=logger_proxy_factory,
            set_user_service_factory=set_user_service_factory,
        ),
    ])
```

а функция `use_factory` может иметь такую реализацию:

``` Python
def use_factory(key: Key[F]) -> Tuple[F, Callable[[F], None]]:
    factory = get_proxy_factory(key)
    
    def set_factory(__factory: F, /) -> None:
        service_locator.set_factory(key, __factory)
        
    return factory, set_factory
```

Она возвращает прокси-фабрику, о которой говорилось ранее, и функцию, позволяющую зарегистрировать фабрику по переданному ключу. Причем прокси-фабрика и функция регистрации привязаны к одному и тому же ключу. Это позволяет явным образом объявить в конструкторе команд инициализации, какие зависимости им нужны и какие зависимости они предоставляют.

Тогда функция инициализации будет выглядеть так:

``` Python
def init() -> None:
    logger_factory, set_logger_factory = use_factory(Key(LoggerFactory))
    user_service_factory, set_user_service_factory = use_factory(Key(UserServiceFactory))
    call_init_commands([
        ConsoleLoggerInitCommand(
            set_logger_factory=set_logger_factory
        ),
        UserServiceImplInitCommand(
            logger_factory=logger_factory,
            set_user_service_factory=set_user_service_factory,
        ),
    ])
```

Можно заметить, что ни компоненты приложения, ни команды инициализации не зависят от локатора служб и, следовательно, от библиотеки, которая его реализует. Сейчас зависимость от библиотеки имеется только в коде инициализации и больше нигде. Следовательно, при таком подходе можно не использовать сторонюю библиотеку, ограничившись своим простым решением. А используемую библиотеку можно будет сравнительно просто заменить на другую, совместимую с таким подходом.

Большим плюсом является то, что команды инициализации не зависят друг от друга, а зависят от абстракций фабрик. Таким образом, их можно легко заменять друг на друга, а так же переиспользовать в других проектах. 

Решение можно считать законченным, однако осталось показать, как эти концепции применяем мы в наших проектах. Об этом и будет следующая, заключительная, часть.

А как вы решаете задачу динамической подгрузки дополнительного функционала? Используете ли вы для этого существующие инструменты или применяете свои решения?
