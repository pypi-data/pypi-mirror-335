from enum import Enum
from typing import List, Union, Any, Type
import inspect
from uvolution.ulogger.handlers import LoggerHandler, FileHandler, FormattingHandler
from rich.console import Console


class LoggerLevels(Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'


class LoggerConfig:
    def __init__(self, levels: List[LoggerLevels]):
        self.levels: List[LoggerLevels] = levels

        self.handlers: List[LoggerHandler] = []

    def add_handler(self, handler: LoggerHandler):
        self.handlers.append(handler)


class Logger:
    def __init__(self, config: LoggerConfig):
        self.config: LoggerConfig = config
        self.console = Console()

    def _trigger_all_handlers(self, data: Any, exclude_types: List[Type[LoggerHandler]] = []):
        for handler in self.config.handlers:
            if type(handler) in exclude_types:
                continue

            handler.trigger(data)

    def _clean_all_handlers(self, exclude_types: List[Type[LoggerHandler]] = [], *args, **kwargs):
        for handler in self.config.handlers:
            if type(handler) in exclude_types:
                continue

            handler.close(*args, **kwargs)

    def _trigger_handler_by_type(self, handler_type: Type[LoggerHandler], data: Any) -> Any:
        for handler in self.config.handlers:
            if isinstance(handler, handler_type):
                return handler.trigger(data)

    def _prelude_triggering(self, data: dict):
        string = self._trigger_handler_by_type(FormattingHandler, data)
        data['string'] = string

        self.console.print(string)

        self._trigger_handler_by_type(FileHandler, string)

        return data

    def _post_triggering(self, data: dict):
        self._trigger_all_handlers(data, [FormattingHandler, FileHandler])

    def close(self):
        self._clean_all_handlers()

    def debug(self, message):
        if LoggerLevels.WARNING not in self.config.levels:
            return

        data = {
            'type': 'debug',
            'exec_ln': inspect.stack()[1][2],
            'invoking': inspect.stack()[1][3],
            'message': message
        }

        data = self._prelude_triggering(data)
        self._post_triggering(data)

    def info(self, message):
        if LoggerLevels.WARNING not in self.config.levels:
            return

        data = {
            'type': 'info',
            'exec_ln': inspect.stack()[1][2],
            'invoking': inspect.stack()[1][3],
            'message': message
        }

        data = self._prelude_triggering(data)
        self._post_triggering(data)

    def warning(self, message):
        if LoggerLevels.WARNING not in self.config.levels:
            return

        data = {
            'type': 'warning',
            'exec_ln': inspect.stack()[1][2],
            'invoking': inspect.stack()[1][3],
            'message': message
        }

        data = self._prelude_triggering(data)
        self._post_triggering(data)

    def error(self, message):
        if LoggerLevels.ERROR not in self.config.levels:
            return

        data = {
            'type': 'error',
            'exec_ln': inspect.stack()[1][2],
            'invoking': inspect.stack()[1][3],
            'message': message
        }

        data = self._prelude_triggering(data)
        self._post_triggering(data)

    def critical(self, message):
        if LoggerLevels.ERROR not in self.config.levels:
            return

        data = {
            'type': 'critical',
            'exec_ln': inspect.stack()[1][2],
            'invoking': inspect.stack()[1][3],
            'message': message
        }

        data = self._prelude_triggering(data)
        self._post_triggering(data)
