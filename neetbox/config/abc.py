from abc import ABC, abstractmethod

from vdtoys.mvc import Singleton


class ConfigInterface(ABC, metaclass=Singleton):
    @abstractmethod
    def __setattr__(self, key, value):
        ...

    @abstractmethod
    def __getattr__(self, key):
        ...

    @abstractmethod
    def update(self, another):
        ...

    @property
    @abstractmethod
    def here(self):
        ...
