Возможные заголовки:
* Python-приложение: расширяем во всех местах 
* Как добавить n+1-ый компонент в Python-приложение

Примеры вопросов после каждой части:
* сталкивались ли вы с подобной проблемой? как решали?
* а используете ли вы DI в своей практике?
* а как вы управляете зависимостями в вашем проекте?

Нормальные введения и заключения для каждой части

Проверить фразы перед каждым кодовым блоком

# Python-приложение: расширяем во всех местах 

## Часть 1

Доброго времени суток! Меня зовут Максим Сахно, я backend-разработчик на языке Python в компании IQtek. Мы занимаемся разработкой продуктов в области IP-телефонии. На своей практике мы столкнулись с такой проблемой, что все клиенты имеют индивидуальные требования к предоставляемому нами ПО и эти требования могут затрагивать произвольные компоненты наших приложений. Именно поэтому мы не можем ограничиться фиксированным набором точек расширения. Нам необходимо иметь возможность заменить любой уже существующий или добавить новый компонент и интегрировать его с другими компонентами системы.

При изучении существующих инструментов мы не нашли такого, которое бы:

* позволяло динамически подгружать компоненты и связывать их друг с другом;

* гарантировало, что при инициализации приложения компоненты получат зависимости нужных типов.

Приятным бонусом было бы отсутствие зависимостей в коде, который не отвечает за инициализацию приложения, от этого инструмента. В данном примере

``` Python
class Service:
    @inject("repository")
    def __init__(repository: Repository) -> None:
        ...
```
компоненту `Service` не нужно знать, каким способом в его конструктор попадет репозиторий. Зависимость от декоратора `inject`, предоставляемого инструментом, явно лишняя. 

Поэтому мы решили создать свой инструмент. В этой статье мы хотим рассказать о том, как и к чему мы в итоге пришли. Для начала давайте рассмотрим такой простой пример, в котором компонент `UserServiceImpl` зависит от компонента `ConsoleLogger`:

``` Python
class UserServiceImpl(UserService):
    __slots__ = ()

    def create(self, email: str) -> User:
        logger = ConsoleLogger("user_service")
        logger.log(f"Creating user with email '{email}'...")
        ...
```

Теперь предположим, что у нас возникла потребность, чтобы логи выводились не в консоль, а в файл. Тогда придется создать класс `FileLogger` и изменить код класса `UserServiceImpl`, а именно в методе `create`  создавать объект класса `FileLogger` вместо `ConsoleLogger`. Разумеется, в достаточно больших проектах любое подобное изменение будет требовать значительных временных затрат.

Проблема состоит в нарушении принципа инверсии зависимостей. Его формулировка звучит так: 

 * Модули верхнего уровня не должны зависеть от модулей нижнего уровня. Оба должны зависеть от абстракции.
 * Абстракции не должны зависеть от деталей. Детали должны зависеть от абстракций.

В нашем примере модуль верхнего уровня `UserServiceImpl`, зависит от модуля нижнего уровня `ConsoleLogger`.

Применение паттерна локатор служб (англ. service locator) позволяет решить обозначенную выше проблему путем создания реестра необходимых зависимостей. В случае использования этого паттерна класс `UserServiceImpl` вместо создания зависимости в виде экземпляра класса `ConsoleLogger` будет запрашивать ее у реестра. Давайте перейдем к реализации данного паттерна на нашем примере.

Для начала выделим абстракцию для логгирования, а именно создадим интерфейс `Logger`:

``` Python
class Logger:
    __slots__ = ()

    def log(self, message: str) -> None:
        raise NotImplementedError()
```

И сделаем так, чтобы `ConsoleLogger` и `FileLogger` реализовывали данный интерфейс. Например, так может выглядеть реализация `ConsoleLogger`:

``` Python
class ConsoleLogger(Logger):
    __slots__ = (
        "__name",
    )

    def __init__(self, name: str) -> None:
        self.__name = name

    def log(self, message: str) -> None:
        sys.stdout.write(f"{self.__name}: {message}\n")
```

Теперь приступим к созданию реестра, который будет хранить зависимости. Одной из самых простых реализаций такого реестра является класс, хранящий объекты по ключам. В качестве ключей могут использоваться, например, строки.

``` Python
class ServiceLocator:
    __slots__ = (
        "__instances",
    )

    def __init__(self) -> None:
        self.__instances: Dict[str, Any] = {}

    def register(self, key: str, instance: Any) -> None:
        self.__instances[key] = instance

    def resolve(self, key: str) -> Any:
        try:
            return self.__instances[key]
        except KeyError:
            raise DependencyResolutionException(key) from None
```

В одном из модулей создадим глобальный зкземпляр, к которому будут обращаться все сущности нашего приложения, которым нужно зарегистрировать или получить зависимость:

``` Python
service_locator = ServiceLocator()
```

Теперь код класса `UserServiceImpl` будет выглядеть следующим образом:

``` Python
class UserServiceImpl(UserService):
    __slots__ = ()

    def create(self, email: str) -> User:
        logger = service_locator.resolve("logger")
        logger.log(f"Creating user with email '{email}'...")
        ...
```

А ниже представлена функция инициализации приложения, которая будет регистрировать в реестр нужные зависимости.

``` Python
def init() -> None:
    service_locator.register("logger", ConsoleLogger("root"))
    service_locator.register("user_service", UserServiceImpl())
```

В случае большого количества зависимостей эта функция может быть разбита на несколько функций меньшего размера, каждая из которых будет заниматься инициализацией своей подсистемы приложения.

Теперь при возникновении потребности выводить логи в файл, а не в консоль, нам необходимо лишь изменить одну строчку в функции конфигурации приложения и изменения вступят в силу для всех компонентов, запрашивающих зависимости через реестр.

Обратите внимание, что теперь благодаря следованию принципу инверсии зависимостей для изменения способа логгирования у класса `UserServiceImpl` у нас нет необходимости изменять его код, что позволяет сократить время, необходимое для внесения изменения в приложение, и избавляет от возможности добавить в этот класс ошибки. Зависимость от абстракции, а не от конкретной реализации, позволяет использовать любую возможную реализацию, не меняя код зависимых компонентов. 

Однако, несмотря на то, что нам удалось таким образом избавиться от жесткой связности между компонентами приложения и сделать его изменение более простым, у текущей реализации данного паттерна есть множество недостатков, но обо всем попорядку. 

Не всегда можно обойтись единственным экземпляром по ключу. В некоторых ситуациях может быть полезно, чтобы при разрешении зависимости каждый раз создавался новый экземпляр объекта или выполнялась какая-то другая логика. Например, в нашем случае нам бы хотелось видеть в логах название того компонента, который осуществил логирование. Для этого нам надо иметь возможность получать экземпляр класса `Logger`, передавая не только ключ, но и имя компонента в качестве параметра. Такую проблему можно решить, если хранить не экземпляры классов, а фабрики для их получения. Этот подход значительно расширяет возможности по получению зависимостей. Используя фабрики, можно реализовать как получение каждый раз единственного экземпляра класса, так и нового, и вообще любую логику по получению зависимостей. Таким образом реализация локатора сервисов примет следующий вид:

``` Python
class ServiceLocator:
    __slots__ = (
        "__factories",
    )

    def __init__(self) -> None:
        self.__factories: Dict[str, Callable[..., Any]] = {}

    def register(self, key: str, factory: Callable[..., Any]) -> None:
        self.__factories[key] = factory

    def resolve(self, __key: str, /, *args: Any, **kwargs: Any) -> Any:
        try:
            factory = self.__factories[__key]
        except KeyError:
            raise DependencyResolutionException(__key) from None

        return factory(*args, **kwargs)
```

А получение зависимости будет выглядеть уже так:

``` Python
class UserServiceImpl(UserService):
    __slots__ = ()

    def create(self, email: str) -> User:
        logger = service_locator.resolve("logger", "user_service")
        logger.log(f"Creating user with email '{email}'...")
        ...
```

Регистрация в свою очередь будет осуществляться таким образом:

``` Python
def init() -> None:

    def get_console_logger(name: str = "root") -> ConsoleLogger:
        return ConsoleLogger(name)

    service_locator.register("logger", get_console_logger)

    user_service = UserServiceImpl()
    service_locator.register("user_service", lambda: user_service)
```

В данном примере благодаря использованию фабрик удалось реализовать различную логику получения зависимостей: по ключу `user_service` клиенты будут получать каждый раз один и тот же экземпляр класса `UserService`, в то время как по ключу `logger` - каждый раз новый экземпляр класса `Logger`.

При работе с достаточно большим проектом, который уже целиком не помещается в голове разработчика, возникнут следующие проблемы. 

При вызове метода `ServiceLocator.resolve` нам неизвестен тип результата, который мы получим. Действительно какой будет тип у переменной `logger` после выполения следующей строчки кода? 

``` Python 
logger = service_locator.resolve("logger", "user_service")
``` 

Для поддержки уже существующего кода и создания нового очень важно быстро находить ответ на вопрос: какой тип имеет объект, на который ссылается та или иная переменная, какие у него есть методы и какие сигнатуры у этих методов? Эта информация необходима для того, чтобы знать, как взаимодействовать с этим объектом. Конечно, тип результата зависит от ключа. В таком случае придется самому разбираться, что же зарегистрировано по необходимому ключу. Можно, конечно, добавить аннотацию к переменной:

``` Python 
logger: Logger = service_locator.resolve("logger", "user_service")
``` 

Но на самом деле так делать не стоит из-за другой проблемы, а именно из-за отсутствия какой-либо гарантии, что по ключу `"logger"` будет получен объект класса `Logger`. Действительно, кто угодно может зарегистрировать по этому ключу что угодно и не сможет удостовериться в том, что не нарушил уже существующий контракт, связанный с используемым ключом. Под контрактом, связанным с ключом, подразумевается сигнатура, которой должны соответствовать все фабрики, которые могут быть зарегистрированы по этому ключу.

И еще одна проблема. А как узнать, не читая документацию и не заглядывая в код фабрик, какие параметры необходимо передать, чтобы разрешить зависимость по конкретному ключу? При такой реализации, к сожалению, никак. В идеале хотелось бы иметь возможность узнать тип результата и список необходимых параметров сразу. Как этого добиться? Ответ: зафиксировать контракт фабрики и сделать его частью ключа. 

Объявим контракт фабрики, которая предоставляет необходимую зависимость. В нашем случае это логгер:

``` Python
class LoggerFactory:
    __slots__ = ()

    def __call__(self, name: str = "root") -> Logger:
        raise NotImplementedError()
```

Создадим реализацию этой фабрики, причем, если мы нарушим контракт, то с помощью средств статического анализа мы сможем об этом узнать.

``` Python
class ConsoleLoggerFactory(LoggerFactory):
    __slots__ = ()

    def __call__(self, name: str = "root") -> Logger:
        return ConsoleLogger(name)
```

Далее нужно каким-либо способом зафиксировать информацию о типе фабрики в ключе. Используем для этой задачи переменные типа (`TypeVar`) из модуля `typing`. Опишем класс ключа следующим образом:

``` Python
F = TypeVar("F", bound=Callable)


class Key(Generic[F]):
    __slots__ = ()

    def __init__(self, factory_type: Type[F], id: str = "") -> None: ...
```

Теперь реализуем класс локатора сервисов так, чтобы по ключу средствами статического анализа можно было определить тип фабрики, которую мы получим при попытке получить зависимость:

``` Python
class ServiceLocator:
    __slots__ = (
        "__factories",
    )

    def __init__(self) -> None:
        self.__factories: Dict[Key[Any], Any] = {}

    def set_factory(self, key: Key[F], factory: F) -> None:
        self.__factories[key] = factory

    def get_factory(self, key: Key[F]) -> F:
        try:
            return self.__factories[key]
        except KeyError:
            raise FactoryNotFoundByKeyException(key) from None
```

Чтобы разобраться, как это работает, давайте рассмотрим пример получения зависимости:

``` Python 
class UserServiceImpl(UserService):
    __slots__ = ()

    def create(self, email: str) -> User:
        logger = service_locator.get_factory(Key(LoggerFactory))("user_service")
        logger.log(f"Creating user with email '{email}'...")
        ...
```

Обратите внимание, что выражение `Key(LoggerFactory)` будет иметь тип `Key[LoggerFactory]`, соответственно результат выражения `service_locator.get_factory(Key(LoggerFactory))` будет иметь тип `LoggerFactory`, а далее мы уже вызываем экземпляр класса `LoggerFactory`, благодаря чему средствами статического анализа кода можно установить, что переменная `logger` будет иметь тип `Logger`, и IDE уже сможет давать нам правильные подсказки и не даст совершить глупые ошибки. То же самое относится и к параметрам, передаваемым в фабрику.

Теперь давайте посмотрим на то, как будет выглядеть регистрация фабрик в обновленной реализации локатора сервисов.

``` Python
def init() -> None:
    service_locator.set_factory(Key(LoggerFactory), ConsoleLoggerFactory())
    service_locator.set_factory(Key(UserServiceFactory), UserServiceFactoryImpl(UserServiceImpl()))
``` 

Снова благодаря тому, что выражение `Key(LoggerFactory)` имеет тип `Key[LoggerFactory]` средствами статического анализа можно вывести то, что второй агрумент должен иметь тип `LoggerFactory`, и не допустить, чтобы по данному ключу была зарегистрирована фабрика другого типа, имеющая другой контракт.

При этом необязательно каждый раз реализовывать интерфейс фабрики вручную, т.к. в большинстве случае можно использовать генераторы реализации фабрик. Например, если нужно, чтобы всегда возвращался один и тот же экземпляр объекта, можно реализовать такой генератор:

``` Python
def generate_singleton_factory(factory_type: Type[F], instance: Any) -> F: ...
```

который по типу фабрики

``` Python
class UserServiceFactory:
    __slots__ = ()

    def __call__(self) -> UserService:
        raise NotImplementedError()
```

сгенерирует реализацию

``` Python
class UserServiceFactoryImpl(UserServiceFactory):
    __slots__ = (
        "__user_service",
    )

    def __init__(self, user_service: UserService) -> None:
        self.__user_service = user_service

    def __call__(self) -> UserService:
        return self.__user_service
``` 

проверяя тип экземпляра и тип результата. Аналогично можно поступить для генерации реализаций фабрик, которые будут вызывать функцию, проверяя сигнатуры фабрики и функции на совместимость.

И тогда регистрация зависимостей будет иметь следующий вид:

``` Python
def init() -> None:

    def get_console_logger(name: str = "root") -> Logger:
        return ConsoleLogger(name)

    logger_factory = generate_function_factory(LoggerFactory, get_console_logger)
    service_locator.set_factory(Key(LoggerFactory), logger_factory)

    user_service_factory = generate_singleton_factory(UserServiceFactory, UserServiceImpl())
    service_locator.register(Key(UserServiceFactory), user_service_factory)
```

Как можно видеть, в таком случае дополнительно нужно только объявлять интерфейсы фабрик. 

## Часть 2

Но до этого мы не говорили о главной проблеме, а именно о том, что зависимости не объявляются явным образом в параметрах конструктора или метода, а скрыты в их реализациях. Даже прочитав их реализации нельзя определить полный список всех зависмостей того или иного компонента, потому что они могут быть скрыты внутри вложенных вызовов. Давайте объявим зависимости явным образом:

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

Однако в тот момент, когда нам может потребоваться фабрика, она может быть еще не зарегистрирована в локаторе сервисов. Для ее решения будем генерировать прокси-фабрики:

``` Python
def get_proxy_factory(key: Key[F]) -> F: ...
```

Функция генерации прокси-фабрики получает на вход ключ, который содержит в себе интерфейс нужной нам фабрики, и возвращает экземпляр такой фабрики. При вызове прокси-фабрика как функции она будет пытаться получить фабрику, которая зарегистрирована по этому ключу в сервис локаторе, и возвращать результат вызова этой фабрики с переданными параметрами. Приведем пример прокси-фабрики, которая будет сгенерирована функцией `get_proxy_factory` по ключу типа `Key[LoggerFactory]`:

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

Это позволит получить нам экземпляр фабрики типа `LoggerFactory` в тот момент, когда она еще не зарегистрирована в локаторе сервисов, и связать наши компоненты при инициализации приложения. Теперь, когда нам доступны прокси-фабрики, перепишем нашу функцию инициализации, используя их:

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

Тогда функция инициализации будет выглядеть следующим образом.

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

Можно заметить, что ни компоненты приложения, ни команды инициализации не зависят от локатора сервисов и, следовательно, от библиотеки, которая его реализует. Сейчас зависимость от библиотеки имеется только в коде инициализации и больше нигде. Следовательно, при таком подходе можно не использовать сторонюю библиотеку, ограничившись своим простым решением. А используемую библиотеку можно будет сравнительно просто заменить на другую, совместимую с таким подходом.

Большим плюсом является то, что команды инициализации не зависят друг от друга, а зависят от абстракций фабрик. Таким образом, их можно легко заменять друг на друга, а так же переиспользовать в других проектах. 

## Часть 3

Теперь мы можем перейти к реализации команды инициализации, которая загружает другие команды инициализации, используя механизм точек доступа в Python.

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
