from abc import ABC, abstractmethod
from typing import Any
from datetime import datetime


class LoggerHandler(ABC):
    @abstractmethod
    def trigger(self, data: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self, *args, **kwargs):
        raise NotImplementedError


class FileHandler(LoggerHandler):
    def __init__(self, filename: str, filemode: str = 'a'):
        self.filename = filename
        self.filemode = filemode
        self.file = open(filename, filemode)

    def trigger(self, data: str) -> None:
        self.file.write(f'{data}\n')

    def close(self):
        self.file.close()


class FormattingHandler(LoggerHandler):
    def __init__(self, format_string: str = '[{time} {type}] at {exec_ln} {invoking}: {message}'):
        self.raw_format_string = format_string

    def trigger(self, data: dict) -> str:
        args = {
            'time': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'type': data.get('type', 'DEBUG'),
            'exec_ln': data.get('exec_ln'),
            'invoking': data.get('invoking'),
            'message': data.get('message', 'None'),
        }

        return self.raw_format_string.format(**args)

    def close(self):
        self.raw_format_string = ''

