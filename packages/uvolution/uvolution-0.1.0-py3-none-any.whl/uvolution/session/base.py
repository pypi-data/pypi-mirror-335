from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass


@dataclass
class SessionConfiguration:



class BaseSession(ABC):
    @abstractmethod
    def set(self, param_name: str, value: str):
        raise NotImplementedError

    def get(self, param_name: str):
        raise NotImplementedError

    def install(self, package_name: str, versions: List[str]):
        raise NotImplementedError

    def run(self, command: str):
        raise NotImplementedError
