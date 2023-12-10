# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230413

import functools
import inspect
import json
from typing import Any, Callable, Dict, List, Optional, Sequence, Union
from uuid import uuid4

from neetbox.logging import logger
from neetbox.utils.formatting import *


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


def _tags_match(search_tags, in_tags) -> bool:
    # check if all tags in f_tags are listed in s_tags
    if type(search_tags) is not list:
        search_tags = [search_tags]
    for _t in search_tags:
        if _t not in in_tags:
            return False
    return True


class Registry(dict):

    """Register Helper Class
    A Register is a 'dict[str:any]'
    Registers are stored in a pool of type dict[str:Register]
    """

    # class level
    _registry_pool: Dict[str, "Registry"] = dict()  # all registeres are stored here

    def __new__(cls, name: str) -> "Registry":
        assert is_pure_ansi(name), "Registry name should not contain non-ansi char."
        name = name.replace(" ", "-")
        if name in cls._registry_pool:
            return cls._registry_pool[name]
        # logger.log(f"Creating Registry for '{name}'")
        instance = dict.__new__(cls)
        cls._registry_pool[name] = instance
        return instance

    # not compatible with python below 3.8
    def __init__(self, name, *args, **kwargs) -> None:
        if "initialized" not in self:
            self["initialized"] = True
            self.name = name

    def _register(
        self,
        what: Any,
        name: Optional[str] = None,
        overwrite: Union[bool, Callable] = lambda x: x + f"_{uuid4()}",
        tags: Optional[Union[str, Sequence[str]]] = None,
    ):
        # if not (inspect.isfunction(what) or inspect.isclass(what)):
        #     logger.warn(f"Registering {type(what)}, which is not a class or a callable.")
        name = name or what.__name__
        if type(tags) is str:
            tags = [tags]
        _endp = _RegEndpoint(what, tags)
        if name in self.keys():
            if isinstance(overwrite, Callable):
                name = overwrite(name)
            elif overwrite == True:
                pass
            else:
                raise RuntimeError(f"")
            logger.warn(f"Overwritting existing '{name}' in Registry '{self.name}'.")
            self[name] = _endp
        else:
            self[name] = _endp
        return what

    def register(
        self,
        *,
        name: Optional[str] = None,
        overwrite: Union[bool, Callable] = lambda x: x + f"_{uuid4()}",
        tags: Optional[Union[str, Sequence[str]]] = None,
    ):
        return functools.partial(self._register, name=name, overwrite=overwrite, tags=tags)

    @classmethod
    def find(
        cls,
        name: Optional[str] = None,
        tags: Optional[Union[str, List[str]]] = None,
    ):
        if not name and not tags:
            # logger.err(
            #     ValueError("Please provide at least the name or the tags you want to find."),
            #     reraise=True,
            # )
            pass
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
        if type(tags) is not list:
            tags = [tags]

        results = {_name: _endp.what for _name, _endp in results if _tags_match(tags, _endp.tags)}
        return results

    def filter(self, tags: Optional[Union[str, Sequence[str]]] = None):
        results = {
            _name: _endp.what for _name, _endp in self._items() if _tags_match(tags, _endp.tags)
        }
        return results

    def __getitem__(self, __key: str) -> Any:
        _v = self.__dict__[__key]
        if type(_v) is _RegEndpoint:
            _v = _v.what
        return _v

    def get(self, key: str, **kwargs):
        if key in self.__dict__:
            _v = self.__dict__[key]
            if type(_v) is _RegEndpoint:
                _v = _v.what
            return _v
        else:
            if "default" in kwargs:
                return kwargs["default"]
            else:
                raise RuntimeError(f"key {key} not found")

    def __setitem__(self, k, v) -> None:
        if not is_pure_ansi(k):
            logger.warn(
                f"None ANSI chars are used for names: {k}. Ignoring anyway"
            )  # todo (visualdust)
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
        return [_item[0] for _item in self.__dict__.items() if type(_item[1]) is _RegEndpoint]

    def values(self):
        return [_item[1].what for _item in self.__dict__.items() if type(_item[1]) is _RegEndpoint]

    def items(self, _real_type=True):
        _legal_items = [_item for _item in self.__dict__.items() if type(_item[1]) is _RegEndpoint]
        if _real_type:
            _legal_items = [(_k, _v.what) for _k, _v in _legal_items if type(_v) is _RegEndpoint]
        return _legal_items

    def _items(self, _real_type=True):
        _legal_items = [_item for _item in self.__dict__.items() if type(_item[1]) is _RegEndpoint]
        if _real_type:
            _legal_items = [(_k, _v) for _k, _v in _legal_items if type(_v) is _RegEndpoint]
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

    __repr__ = __str__
