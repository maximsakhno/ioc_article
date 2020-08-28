# IOC

Рассмотрим такой простой пример.

``` Python
class UserServiceImpl(UserService):
    __slots__ = ()

    def create(self, email: str) -> User:
        logger = ConsoleLogger("user_service")
        logger.log(f"Creating user with email '{email}'...")
        ...
```

Теперь предположим, что у нас возникла потребность, чтобы логи выводились не в консоль, а в файл. Тогда придется создать класс `FileLogger` и изменить код класса `UserServiceImpl`, а именно в методе `create`  создавать объект класса `FileLogger` вместо `ConsoleLogger`. В случае, если размер приложения уже довольно велик, а счет мест, где непосредственно создается объект класса `ConsoleLogger` идет уже на десятки, если не сотни, то его замена на `FileLogger` может стать проблематичной. В случае, когда все зависимости создаются таким образом дальнейшее развитие проекта может стать невозможным, так как любое изменение будет требовать значительных временных затрат.

Проблема состоит в нарушении принципа инверсии зависимостей. Его формулировка звучит так: 

 * Модули верхнего уровня не должны зависеть от модулей нижнего уровня. Оба должны зависеть от абстракции.
 * Абстракции не должны зависеть от деталей. Детали должны зависеть от абстракций.

В нашем примере модуль верхнего уровня `UserServiceImpl`, зависел от модуля нижнего уровня `ConsoleLogger`.

Использование паттерна локатор служб (англ. service locator) позволяет решить обозначенную выше проблему путем создания реестра необходимых зависимостей. Если ранее `UserServiceImpl` сам непостредственно создавал себе необходимые зависимости (в данном примере `ConsoleLogger`), то теперь он будет запрашивать их у рееста.
<сделать плавный переход>
Но сперва необходимо выделить абстракцию для логгирования, а именно создадим интерфейс `Logger`.

``` Python
class Logger:
    __slots__ = ()

    def log(self, message: str) -> None:
        raise NotImplementedError()
```

И добавим его реализации. Например, так может выглядеть реализация `ConsoleLogger`.

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

Теперь нам необходимо создать реестр хранящий зависимости. Одной из самых простых реализаций такого реестра может являться класс, хранящий объекты по ключам. В качестве ключей могут использоваться, например, строки.

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

В одном из модулей создадим глобальный зкземпляр, к которому будут обращаться все модули нашего приложения, которым нужно зарегистрировать или разрешить зависимость.

``` Python
service_locator = ServiceLocator()
```

В таком случае получение зависимости будет выглядеть следующим образом.

``` Python
class UserServiceImpl(UserService):
    __slots__ = ()

    def create(self, email: str) -> User:
        logger = service_locator.resolve("logger")
        logger.log(f"Creating user with email '{email}'...")
        ...
```

А ниже представлена регистрация зависимостей, которая будет осуществляться при инициализации прилоежния.

``` Python
def init() -> None:
    service_locator.register("logger", ConsoleLogger("root"))
    service_locator.register("user_service", UserServiceImpl())
```

Причем регистрация зависимостей приложения может быть разделена на несколько функций.

Теперь, для того чтобы изменть наше приложение таким образом, чтобы логгирование осуществлялось в файл, а не в консоль, достаточно изменть одну строчку в функции инициализации нашего приложения и изменения вступят в силу для всех модулей, которые запрашивают зависимость через локатор служб. 

Еще одним преимуществом следования принципу инверсии зависимостей является то, что в классе `UserServiceImpl` для изменения способа логирования не пришлось изменять его код, а это, в свою очередь, помогает не только сэкономить время, но и избавляет от возможности добавить в класс новые ошибки. Зависимость от абстракции, а не от конкретной реализации, позволяет использовать любую возможную реализацию, не меняя код зависимых сущностей. 

Однако, несмотря на то, что нам удалось таким образом избавиться от жесткой связности между компонентами приложения и сделать его изменение более простым, у текущей реализации данного паттерна есть множество недостатков, но обо всем попорядку. 

Не всегда можно обойтись одним экземпляром по ключу. В нашем примере было бы удобно иметь возможность получать экземпляр логгера, передавая в качестве параметра его имя. Такую проблему можно решить, если хранить не экземпляры классов, а фабрики для их получения. Этот подход значительно расширяет возможности по созданию зависимостей. Используя фабрики можно реализовать, как получение каждый раз единственного экземпляра класса, так и нового и вообще любую логику по получению зависимостей. Реализация локатора сервисов примет следующий вид.

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

А получение зависимости будет выглядеть уже так.

``` Python
class UserServiceImpl(UserService):
    __slots__ = ()

    def create(self, email: str) -> User:
        logger = service_locator.resolve("logger", "user_service")
        logger.log(f"Creating user with email '{email}'...")
        ...
```

Регистрация в свою очередь будет осуществляться уже так.

``` Python
def init() -> None:

    def get_console_logger(name: str = "root") -> ConsoleLogger:
        return ConsoleLogger(name)

    service_locator.register("logger", get_console_logger)

    user_service = UserServiceImpl()
    service_locator.register("user_service", lambda: user_service)
```

Как можно заметить в данном примере благодаря использованию фабрик удалось реализовать получение нового экземпляра по имени в случае логгера, так и получение единственного экземпляра для сервиса пользователей.

При работе с достаточно большим проектом, который уже целиком не помещается в голове разработчика, возникнут следующие проблемы. 

Неизвестный тип результата вызова метода `ServiceLocator.resolve`. Действительно какой будет тип у переменной `logger` после выполения следующей строчки кода? 

``` Python 
logger = service_locator.resolve("logger", "user_service")
``` 

А эта информация очень важна. Для того чтобы вносить изменения в проект необходимо знать как работать с уже существующими сущностями. Знать какие имеются аттрибуты у объекта на который ссылается переменная, какие у этого объекта есть методы и какие у них сигнатуры. Иными словами знать, какой тип имеет та или иная переменная.

Конечно тип результата зависит от ключа. В таком случае придется потратить кучу времени читая код проекта в поисках, что же зарегистрировано по необходимому ключу.

Можно конечно добавить аннотацию к переменной. 

``` Python 
logger: Logger = service_locator.resolve("logger", "user_service")
``` 

Но на самом деле так делать не стоит из-за другой проблемы, а именно отсутствие какой либо гарантии, что по ключу `"logger"` будет получен объект класса `Logger`. Действительно, кто угодно может зарегистрировать по этому ключу, что угодно и не сможет удостовериться в том, что не нарушил уже существующий контракт, связанный с используемым ключом. Под контрактом связанным с ключом подразумевается сигнатура, которой должны соответствовать все фабрики, которые могут быть зарегистрированы по этому ключу.

И еще одна проблема. А как узнать, не тратя кучу времени на изучение исходного кода проекта или чтение документации, какие параметры необходимо передать, чтобы разрешить зависимость по конкретному ключу? При такой реализации, к сожалению, никак.

В идеале хотелось бы иметь возможность узнать тип результата и список необходимых параметров сразу на месте, не тратя время на поиск ответов в коде проекта. Как этого добиться? Ответ: зафиксировать контракт фабрики и сделать его частью ключа. 

Объявим контракт фабрики, которая предоставляет необходимую зависимость, в нашем случае это будет логгер.

``` Python
class LoggerFactory:
    __slots__ = ()

    def __call__(self, name: str = "root") -> Logger:
        raise NotImplementedError()
```

Создадим реализацию этой фабрики, а средства статического анализа не позволят нам нарушить объявленный нами ранее контракт.

``` Python
class ConsoleLoggerFactory(LoggerFactory):
    __slots__ = ()

    def __call__(self, name: str = "root") -> Logger:
        return ConsoleLogger(name)
```

Далее нужно каким либо способом зафиксировать информацию о типе фабрики в ключе. Используем для этой задачи переменные типа (`TypeVar`) из модуля `typing`. Опишем класс ключа следующим образом.

``` Python
F = TypeVar("F", bound=Callable)


class Key(Generic[F]):
    __slots__ = ()

    def __init__(self, factory_type: Type[F], id: str = "") -> None: ...
```

Теперь реализуем класс локатора сервисов, так чтобы по ключу средствами статического анализа можно было определить тип фабрики котрую мы получим при попытке получить зависимость.

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

Чтобы разобраться как это работает давайте рассмотрим пример получения зависимости.

``` Python 
class UserServiceImpl(UserService):
    __slots__ = ()

    def create(self, email: str) -> User:
        logger = service_locator.get_factory(Key(LoggerFactory))("user_service")
        logger.log(f"Creating user with email '{email}'...")
        ...
```

Обратите внимание, что выражение `Key(LoggerFactory)` будет иметь тип `Key[LoggerFactory]`, соответственно результат выражения `service_locator.get_factory(Key(LoggerFactory))` будет иметь тип `LoggerFactory`, а далее мы уже вызываем экземпляр класса `LoggerFactory`, благодаря чему средствами статического анализа кода можно установить, что переменная `logger` будет иметь тип `Logger` и IDE уже сможет давать нам правильные подсказки и не даст совершить глупые ошибки, что позволит сэкономить время. То же самое относится и к параметрам передаваемым в фабрику.

Теперь давайте посмотрим на то, как будет выглядеть регистрация фабрик в обновленной реализации локатора сервисов.

``` Python
def init() -> None:
    service_locator.set_factory(Key(LoggerFactory), ConsoleLoggerFactory())
    service_locator.set_factory(Key(UserServiceFactory), UserServiceFactoryImpl(UserServiceImpl()))
``` 

Снова благодаря тому, что выражение `Key(LoggerFactory)` имеет тип `Key[LoggerFactory]` средствами статического анализа можно вывести, то что второй агрумент должен иметь тип `LoggerFactory` и не допустить, чтобы по данному ключу была зарегистрирована фабрика другого типа имеющая другой контракт.

К аргументам против данного решения можно отнести то, что теперь для каждой зависимости нужно писать фабрики, что будет отнимать время. Однако потраченное время сейчас сэкономит несоизмеримо больше времени в будущем. Причем можно реализовать различные генераторы реализаций однотипных фабрик. Например, если нужно чтобы всегда возвращался один и тот же экземпляр объекта можно реализовать генератор фабрик

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

проверяя тип экземпляра и тип результата.

Аналогично можно поступить для генерации фабрик, которые будут вызывать функцию, проверяя сигнатуры фабрики и функции на совместимость разумеется.

И тогда регистрация зависимостей будет иметь следующий вид.

``` Python
def init() -> None:

    def get_console_logger(name: str = "root") -> Logger:
        return ConsoleLogger(name)

    logger_factory = generate_function_factory(LoggerFactory, get_console_logger)
    service_locator.set_factory(Key(LoggerFactory), logger_factory)

    user_service_factory = generate_singleton_factory(UserServiceFactory, UserServiceImpl())
    service_locator.register(Key(UserServiceFactory), user_service_factory)
```

Как можно видеть в таком случае дополнительно нужно только объявлять интерфейсы фабрик.

Но до этого мы не говорили о главной проблеме, а именно о том, что зависимости не объявляются явным образом в параметрах конструктора или метода, а скрыты в их реализациях. Даже прочитав их реализации нельзя определить полный список всех зависмостей той или иной сущности, потому что они могут быть скрыты внутри вложенных вызовов. Это плохо еще и потому, что не нужное чтение кода занимает значительную часть времени, которое могло бы быть потрачено на разработку. Так давайте же объявим зависимости явным образом.

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

Но тут возникает проблема. Она заключается в том, что в тот момент когда нам может потребоваться фабрика, она может быть еще не зарегистрирована в локаторе сервисов. Для ее решения будем генерировать прокси фабрики.

``` Python
def get_factory_proxy(key: Key[F], service_locator: ServiceLocator) -> F: ...
```

Данная функция по ключу типа `Key[LoggerFactory]` сгенерирует фабрику с подобной реализацией. 

``` Python
class LoggerFactoryProxy(LoggerFactory):
    __slots__ = (
        "__service_locator",
        "__key",
    )

    def __init__(self, service_locator: ServiceLocator, key: Key[LoggerFactory]) -> None:
        self.__service_locator = service_locator
        self.__key = key

    def __call__(self, name: str = "root") -> Logger:
        return self.__service_locator.get_factory(self.__key)(name)
```

Это позволит получить нам экземпляр фабрики типа `LoggerFactory` в тот момент, когда она еще не зарегистрирована в локаторе сервисов и связать наши компоненты при инициализации приложения.

``` Python
def init() -> None:
    logger_factory_proxy = get_factory_proxy(Key(LoggerFactory), service_locator)
    user_service = UserServiceImpl(logger_factory_proxy)
    service_locator.set_factory(Key(UserServiceFactory), UserServiceFactoryImpl(user_service))
```

Но остается еще одна проблема. Нет никакой гарантии, что после инициализации приложения `LoggerFactory`, от которой зависит `UserServiceImpl` будет зарегистрирована. О таких вещах лучше узнавать, если не при помощи статического анализа, то хотя бы на этапе запуска приложения. Да и `UserServiceImpl` требуется не `LoggerFactory`, а непосредственно `Logger`. Таким образом мы приходим к тому, что внедрение зависимости должно происходить на один уровень выше, а именно в командах инициализации.

Опишем интерфейс такой команды.

``` Python
class InitCommand:
    __slots__ = ()

    def __call__(self) -> None:
        raise NotImplementedError()
```

Реализация такой команды, регистрирующая `LoggerFactory`.

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

Обратите внимание, что тот факт, что эта команда регистрирует `LoggerFactory` указано явным образом в конструкторе этой команды. Но подроблнее на этом остановимся позже.

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

При этом `UserServiceImpl` зависит уже не от `LoggerFactory`, а непосредственно от `Logger`. Что и дает нам гарантию того, что после инициализации приложения необходимые зависимости будут зарегистрированы, в противном случае мы получим ошибку на этапе инициализации приложения.

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

Инициализация приложения может выглядеть следующим образом.

``` Python 
def init() -> None:
    logger_factory, set_logger_factory = use_factory(Key(LoggerFactory), service_locator)
    user_service_factory, set_user_service_factory = use_factory(Key(UserServiceFactory), service_locator)
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

Тут функция `use_factory` может быть объявлена следующим образом.

``` Python
def use_factory(key: Key[F], service_locator: ServiceLocator) -> Tuple[F, Callable[[F], None]]:
    factory = get_factory_proxy(key, service_locator)
    
    def set_factory(__factory: F, /) -> None:
        service_locator.set_factory(key, __factory)
        
    return factory, set_factory
```

Она возвращает прокси фабрику, о которой говорилось ранее и функцию позволяющую зарегистрировать фабрику, которую в свою очередь будет вызывать прокси фабрика. Причем прокси фабрика и функция регистрации привязаны к одному и тому же ключу. Это позволяет явным образом объявить в конструкторе команд инициализации, какие зависимости им нужны и какие зависимости они предоставляют.

Тогда функция инициализации будет выглядеть следующим образом.

``` Python
def init() -> None:
    logger_factory, set_logger_factory = use_factory(Key(LoggerFactory), service_locator)
    user_service_factory, set_user_service_factory = use_factory(Key(UserServiceFactory), service_locator)
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

Можно заметить, что ни компоненты приложения, ни команды инициализации не зависят от локатора сервисов и следовательно от библиотеки которая его реализует, как это часто бывает при использовании DI фреймворков, когда их компоненты (например декораторы для инъекции зависимостей) используются во всех частях проекта. Тут же зависимость от библиотеки имеется только в коде инициализации и больше нигде. Следовательно при таком подходе можно не использовать сторонюю библиотеку ограничившись своим простым решением. А испльзуемую библиотеку можно будте сравнительно просто заменить на другую совместимую с таким подходом.

Большим плюсов является то, что команды инициализации не зависят друг от друга, а зависят от абстракций фабрик. Таким образом их можно легко заменять друг на друга, а так же переиспользовать в других проектах. 

Наиболее полно преимущества данного подхода раскрывает задача, когда, например, Вы предоставляете Ваше приложение разным клиентам и у этих клиентов есть специфичные для них потребности. Тут уже не получится обойтись инъкцией зависимостей руками или заранее объявить зависимости в глобальном модуле, да и складывать в основную кодовую базу проекта код специфичный для разных клиентов не разумно. Тогда набор используемых команд инициализации может быть вынесен в конфиг, а у каждого клиента будет свой конфиг, в котором помимо стандартного набора команд инициализаи будут и специфичные для него. К тому же дополнительные команды инициализации можно будте подгружать через механизм точек входа. Таким образом Вы сможете неограниченно расширять возможности Вашего приложения.
