from abc import ABC, abstractmethod

from neetbox.utils.mvc import Singleton


class ConfigInterface(ABC, metaclass=Singleton):
    @abstractmethod
    def __setattr__(self, key, value):
        ...

    @abstractmethod
    def __getattr__(self, key):
        pass
