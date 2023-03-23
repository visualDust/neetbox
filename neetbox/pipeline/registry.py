from neetbox.logging import logger
from neetbox.utils import utils
from typing import Optional, Union, Sequence
import inspect
import json
import functools
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

_registry_pool: Dict[str, "Registry"] = dict()  # all registeres are stored here

class Registry(dict):
    """Register Helper Class
    A Register is a 'dict[str:any]'
    Registers are stored in a pool of type dict[str:Register]
    """

    def __new__(cls, name: str, filter_strs: any = None) -> "Registry":
        assert utils.is_pure_ansi(
            name
        ), "Registry name should not contain non-ansi char."
        if name in _registry_pool:
            return _registry_pool[name]
        instance = dict.__new__(cls)
        _registry_pool[name] = instance
        return instance

    # not compatible with python below 3.8
    def __init__(
        self, name: str, *, filter_strs: Optional[Union[str, Sequence[str]]] = None
    ) -> None:
        super().__init__()
        self.name = name
        if filter_strs:
            self.filter_strs = (
                [filter_strs] if isinstance(filter_strs, str) else filter_strs
            )
            self.filter_strs = dict()

    def _register(
        self,
        what: any,
        force: bool = False,
        name: Optional[str] = None,
        **filter_strs,
    ):
        if not (inspect.isfunction(what) or inspect.isclass(what)):
            logger.warn("Registering {type(what)}, which is not a class or a callable.")
        name = name or what.__name__
        if not force and name in self.keys():
            raise ValueError(f"{name} already exists in Registry:{self.name}")

        if filter_strs:
            if not hasattr(self, "filter_strs"):
                raise ValueError(
                    "Registry `{}` does not have `filter_strs`.".format(self.name)
                )
            for k in filter_strs.keys():
                if k not in self.filter_strs:
                    raise ValueError(
                        "Registry `{}`: 'filter_strs' does not has expected key {}.".format(
                            self.name, k
                        )
                    )
            self.filter_strs[name] = [
                filter_strs.get(k, None) for k in self.filter_strs
            ]
        elif hasattr(self, "filter_strs"):
            self.filter_strs[name] = [None] * len(self.filter_strs)

        self[name] = what
        return what

    def register(
        self, force: bool = False, name: Optional[str] = None, **filter_strs
    ) -> Callable:
        return functools.partial(self._register, force=force, name=name, **filter_strs)

    def register_all(
        self,
        modules: Sequence[Callable],
        names: Optional[Sequence[str]] = None,
        filter_strs: Optional[Sequence[Dict[str, Any]]] = None,
        force: bool = False,
    ) -> None:
        _names = names if names else [None] * len(modules)
        _info = filter_strs if filter_strs else [{}] * len(modules)
        for module, name, info in zip(modules, _names, _info):
            self._register(module, force=force, name=name, **info)

    def merge(
        self,
        others: Union["Registry", List["Registry"]],
        force: bool = False,
    ) -> None:
        if not isinstance(others, list):
            others = [others]
        if not isinstance(others[0], Registry):
            raise TypeError(
                "Expect `Registry` type, but got {}".format(type(others[0]))
            )
        for other in others:
            modules = list(other.values())
            names = list(other.keys())
            self.register_all(modules, force=force, names=names)
            
            
    @classmethod
    def get_all_registries():
        return _registry_pool
    
    @classmethod
    def _find_global_with_name(name:str, default = None):
        for reg_name, reg in _registry_pool.values():
            private_sign = '__'
            if not reg_name.startswith(private_sign):
                if name in reg:
                    return reg[name]
        return default
    
    @classmethod
    def _find_global_with_filter_strs(fileters:List[str]):
        pass

    def __getitem__(self, __key: str) -> Any:
        return super().__getitem__(__key)

    def __setitem__(self, k, v) -> None:
        assert utils.is_pure_ansi(
            k
        ), "Only ANSI chars are allowed for registering things."
        super().__setitem__(k, v)

    def __str__(self) -> str:
        s = json.dumps(
            self,
            indent=4,
            ensure_ascii=False,
            sort_keys=False,
            separators=(",", ":"),
            default=str,
        )
        return s
