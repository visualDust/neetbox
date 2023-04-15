# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230413

from neetbox.logging import logger
from neetbox.utils.utils import *
from typing import Optional, Union, Sequence
import inspect
import json
import functools
from typing import Any, Callable, Dict, List, Optional, Sequence, Union


class _RegEndpoint:
    def __init__(self, what, tags=None):
        """Generate a massive type which contains both the regietered object and it's tags

        Args:
            what (_type_): The object being registered
            tags (_type_, optional): The tags. Defaults to None.
        """
        self.what = what
        self.tags = tags

    def __str__(self) -> str:
        return f"{self.what} with tags: {self.tags}"


class Registry(dict):

    """Register Helper Class
    A Register is a 'dict[str:any]'
    Registers are stored in a pool of type dict[str:Register]
    """

    # class level
    _registry_pool: Dict[str, "Registry"] = dict()  # all registeres are stored here

    def __new__(cls, name: str) -> "Registry":
        assert is_pure_ansi(name), "Registry name should not contain non-ansi char."
        if name in cls._registry_pool:
            return cls._registry_pool[name]
        logger.log(f"Creating Registry for '{name}'")
        instance = dict.__new__(cls)
        cls._registry_pool[name] = instance
        return instance

    # not compatible with python below 3.8
    def __init__(self, name, *args, **kwargs) -> None:
        if not "initialized" in self:
            self["initialized"] = True
            self.name = name

    def _register(
        self,
        what: Any,
        name: Optional[str] = None,
        force: bool = True,
        tags: Optional[Union[str, Sequence[str]]] = None,
    ):
        # if not (inspect.isfunction(what) or inspect.isclass(what)):
        #     logger.warn(f"Registering {type(what)}, which is not a class or a callable.")
        name = name or what.__name__
        if type(tags) is str:
            tags = [tags]
        _endp = _RegEndpoint(what, tags)
        if name in self.keys():
            if not force:
                logger.warn(
                    f"{name} already exists in Registry:{self.name}. If you want to overwrite, try to register with 'force=True'"
                )
            else:
                logger.warn(
                    f"Overwritting existing '{name}' in Registry '{self.name}'."
                )
                self[name] = _endp
        else:
            self[name] = _endp
        return what

    def register(
        self,
        *,
        name: Optional[str] = None,
        force: bool = True,
        tags: Optional[Union[str, Sequence[str]]] = None,
    ):
        return functools.partial(self._register, name=name, force=force, tags=tags)

    @classmethod
    def find(
        cls,
        name: Optional[str] = None,
        tags: Optional[Union[str, List[str]]] = None,
    ):
        if not name and not tags:
            logger.err(
                ValueError(
                    "Please provide at least the name or the tags you want to find."
                ),
                reraise=True,
            )
        results = []
        # filter name
        for reg_name, reg in cls._registry_pool.items():
            private_sign = "__"
            if not reg_name.startswith(private_sign):
                if not name:
                    results += [(_n, _o) for _n, _o in reg.items(_real_type=False)]
                elif name in reg:
                    results.append((name, reg[name]))

        # filter tags
        if type(tags) is str:
            tags = [tags]

        def _tags_match(f_tags, s_tags) -> bool:
            # check if all tags in f_tags are listed in s_tags
            for _t in f_tags:
                if _t not in s_tags:
                    return False
            return True

        results = {
            _name: _endp.what
            for _name, _endp in results
            if _tags_match(tags, _endp.tags)
        }
        return results

    def __getitem__(self, __key: str) -> Any:
        _v = self.__dict__[__key]
        if type(_v) is _RegEndpoint:
            _v = _v.what
        return _v

    def __setitem__(self, k, v) -> None:
        assert is_pure_ansi(k), "Only ANSI chars are allowed for registering things."
        self.__dict__[k] = v

    def clear(self):
        return self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return [
            _item[0]
            for _item in self.__dict__.items()
            if type(_item[1]) is _RegEndpoint
        ]

    def values(self):
        return [
            _item[1].what
            for _item in self.__dict__.items()
            if type(_item[1]) is _RegEndpoint
        ]

    def items(self, _real_type=True):
        _legal_items = [
            _item for _item in self.__dict__.items() if type(_item[1]) is _RegEndpoint
        ]
        if _real_type:
            _legal_items = [
                (_k, _v.what) for _k, _v in _legal_items if type(_v) is _RegEndpoint
            ]
        return _legal_items

    def pop(self, *args):
        return self.__dict__.pop(*args)

    def __cmp__(self, dict_):
        return self.__cmp__(self.__dict__, dict_)

    def __contains__(self, item):
        return item in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)

    def __str__(self) -> str:
        return json.dumps(
            dict(self.items()),
            indent=4,
            ensure_ascii=False,
            sort_keys=False,
            separators=(",", ":"),
            default=str,
        )
