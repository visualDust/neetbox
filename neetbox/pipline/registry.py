from neetbox.logging import get_logger
from neetbox.utils import utils
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

_registry_pool = {}  # str:Registry

class Config(dict):
    def __init__(self, name, age):
      self.name = name
      self.age = age


class Registry(dict):
    def __new__(cls, name: str) -> "Registry":
        assert utils.is_pure_ansi(name)
        if name in _registry_pool:
            return _registry_pool[name]
        instance = dict.__new__(cls)
        Registry.children[name] = instance
        return instance
    
    # not compatible with python below 3.8
    def __init__(
        self, name: str, *, extra_field: Optional[Union[str, Sequence[str]]] = None
    ) -> None:
        super().__init__()
        self.name = name
        if extra_field:
            self.extra_field = (
                [extra_field] if isinstance(extra_field, str) else extra_field
            )
            self.extra_info = dict()