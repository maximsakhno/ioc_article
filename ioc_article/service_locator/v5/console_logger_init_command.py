from ioc_article.logger import (
    LoggerFactory,
)
from ..v2.Key import Key
from ..v2.service_locator import service_locator
from ..v4.use_factory import use_factory
from ..v4.ConsoleLoggerInitCommand import ConsoleLoggerInitCommand


_, set_logger_factory = use_factory(Key(LoggerFactory), service_locator)
init_command = ConsoleLoggerInitCommand(set_logger_factory)
