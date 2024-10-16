# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20230413

import functools
import json
from typing import Any, Callable, Dict, List, Optional, Sequence, Union
from uuid import uuid4


class _RegEndpoint:
    def __init__(self, what, tags=None):
        """Generate a massive type which contains both the registered object and its tags

        Args:
            what (Any): The object being registered
            tags (Optional[Union[str, Sequence[str]]], optional): The tags. Defaults to None.
        """
        self.what = what
        self.tags = tags

    def __str__(self) -> str:
        return f"{self.what} with tags: {self.tags}"


def _tags_match(search_tags, in_tags) -> bool:
    """Check if all tags in search_tags are listed in in_tags."""
    if not isinstance(search_tags, list):
        search_tags = [search_tags]
    for _t in search_tags:
        if _t not in in_tags:
            return False
    return True


class Registry(dict):
    """Register Helper Class
    A Registry is a 'dict[str:any]'
    Registries are stored in a pool of type dict[str:Registry]
    """

    # Class-level registry pool
    _registry_pool: Dict[str, "Registry"] = dict()

    def __new__(cls, name: str) -> "Registry":
        if name in cls._registry_pool:
            return cls._registry_pool[name]
        instance = dict.__new__(cls)
        cls._registry_pool[name] = instance
        return instance

    def __init__(self, name) -> None:
        if "initialized" not in self:
            self["initialized"] = True
            self.name = name

    def _register(
        self,
        what: Any,
        name: Optional[str] = None,
        overwrite: Union[bool, Callable[[str], str]] = lambda x: x + f"_{uuid4()}",
        tags: Optional[Union[str, Sequence[str]]] = None,
    ):
        name = name or what.__name__
        if isinstance(tags, str):
            tags = [tags]
        _endp = _RegEndpoint(what, tags)
        if name in self.keys():
            if callable(overwrite):
                name = overwrite(name)
            elif overwrite is True:
                pass
            else:
                raise RuntimeError("Unknown overwrite type.")
            self[name] = _endp
        else:
            self[name] = _endp
        return what

    def register(
        self,
        *,
        name: Optional[str] = None,
        overwrite: Union[bool, Callable[[str], str]] = lambda x: x + f"_{uuid4()}",
        tags: Optional[Union[str, Sequence[str]]] = None,
    ):
        def decorator(what):
            self._register(what, name=name, overwrite=overwrite, tags=tags)
            return what
        return decorator

    @classmethod
    def find(
        cls,
        name: Optional[str] = None,
        tags: Optional[Union[str, List[str]]] = None,
    ):
        if not name and not tags:
            raise ValueError("Please provide at least the name or the tags you want to find.")
        results = []
        # Filter by name
        for reg_name, reg in cls._registry_pool.items():
            private_sign = "__"
            if not reg_name.startswith(private_sign):
                if not name:
                    results += [(_n, _o) for _n, _o in reg.items(_real_type=False)]
                elif name in reg:
                    results.append((name, reg[name]))
        # Filter by tags
        if not isinstance(tags, list):
            tags = [tags]
        results = {
            _name: _endp.what
            for _name, _endp in results
            if _tags_match(tags, _endp.tags)
        }
        return results

    def filter(self, tags: Optional[Union[str, Sequence[str]]] = None):
        results = {
            _name: _endp.what
            for _name, _endp in self._items()
            if _tags_match(tags, _endp.tags)
        }
        return results

    def __getitem__(self, __key: str) -> Any:
        _v = self.__dict__[__key]
        if isinstance(_v, _RegEndpoint):
            _v = _v.what
        return _v

    def get(self, key: str, **kwargs):
        if key in self.__dict__:
            _v = self.__dict__[key]
            if isinstance(_v, _RegEndpoint):
                _v = _v.what
            return _v
        else:
            if "default" in kwargs:
                return kwargs["default"]
            else:
                raise RuntimeError(f"Key '{key}' not found")

    def __setitem__(self, k, v) -> None:
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
            if isinstance(_item[1], _RegEndpoint)
        ]

    def values(self):
        return [
            _item[1].what
            for _item in self.__dict__.items()
            if isinstance(_item[1], _RegEndpoint)
        ]

    def items(self, _real_type=True):
        _legal_items = [
            _item
            for _item in self.__dict__.items()
            if isinstance(_item[1], _RegEndpoint)
        ]
        if _real_type:
            _legal_items = [
                (_k, _v.what)
                for _k, _v in _legal_items
                if isinstance(_v, _RegEndpoint)
            ]
        return _legal_items

    def _items(self, _real_type=True):
        _legal_items = [
            _item
            for _item in self.__dict__.items()
            if isinstance(_item[1], _RegEndpoint)
        ]
        if _real_type:
            _legal_items = [
                (_k, _v)
                for _k, _v in _legal_items
                if isinstance(_v, _RegEndpoint)
            ]
        return _legal_items

    def pop(self, *args):
        return self.__dict__.pop(*args)

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