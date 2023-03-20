from neetbox.logging import get_logger
from neetbox.utils import utils
from typing import Any, Callable, Dict, List, Optional, Sequence, Union


class Config(dict):
    def __init__(self, name, age):
        self.name = name
        self.age = age


_registry_pool: Dict[str, "Registry"] = dict()  # all registeres are stored here
    
class Registry(dict):
    """Register Helper Class
    A Register is a 'dict[str:any]'
    Registers are stored in a pool of type dict[str:Register]
    """

    def __new__(cls, name: str, filter_strs: Any = None) -> "Registry":
        assert utils.is_pure_ansi(name)
        if name in cls._registry_pool:
            return cls._registry_pool[name]
        instance = dict.__new__(cls)
        Registry._registry_pool[name] = instance
        return instance

    # not compatible with python below 3.8
    def __init__(
        self, name: str, *, filter_strs: Optional[Union[str, Sequence[str]]] = None
    ) -> None:
        super().__init__()
        self.name = name
        self.registed: list = []
        if filter_strs:
            self.filter_strs = (
                [filter_strs] if isinstance(filter_strs, str) else filter_strs
            )
            self.extra_info = dict()

    def __getitem__(self, __key: str) -> Any:
        return super().__getitem__(__key)

    def __setitem__(self, k, v) -> None:
        assert utils.is_pure_ansi(k)
        super().__setitem__(k, v)
