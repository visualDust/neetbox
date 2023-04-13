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


class Registry(dict):
    """Register Helper Class
    A Register is a 'dict[str:any]'
    Registers are stored in a pool of type dict[str:Register]
    """

    # class level
    _registry_pool: Dict[str, "Registry"] = dict()  # all registeres are stored here

    # instance level
    initialized: bool = False

    def __new__(cls, name: str) -> "Registry":
        assert is_pure_ansi(name), "Registry name should not contain non-ansi char."
        if name in cls._registry_pool:
            return cls._registry_pool[name]
        logger.log(f"Creating Registry for {cls}")
        instance = dict.__new__(cls)
        cls._registry_pool[name] = instance
        return instance

    # not compatible with python below 3.8
    def __init__(self, name: str) -> None:
        if not self.initialized:
            # do initializations
            self.name = name
            self.initialized = True

    def _register(
        self,
        what: Any,
        name: Optional[str] = None,
        force: bool = False,
        tags: Optional[Union[str, Sequence[str]]] = None,
    ):
        if not (inspect.isfunction(what) or inspect.isclass(what)):
            logger.warn("Registering {type(what)}, which is not a class or a callable.")
        name = name or what.__name__
        if type(tags) is str:
            tags = [tags]
        if name in self.keys():
            if not force:
                logger.warn(
                    f"{name} already exists in Registry:{self.name}. If you want to overwrite, try to register with 'force=True'"
                )
            else:
                logger.warn(f"Overwritting: {name} existed in Registry:{self.name}.")
                self[name] = (what, tags)
        else:
            self[name] = (what, tags)
        return what

    def register(
        self,
        *,
        name: Optional[str] = None,
        force: bool = False,
        tags: Optional[Union[str, Sequence[str]]] = None,
    ) -> Callable:
        return functools.partial(
            self._register, name=name, force=force, tags=tags
        )

    def register_all(
        self,
        what: Union[Dict, Sequence[Callable]],
        names: Optional[Sequence[str]] = None,
        tags: Optional[Union[str, Sequence[str]]] = None,
        force: bool = False,
    ) -> None:
        if type(what) is dict:
            _names = what.keys()
            what = what.values()
        if type(what) is list:
            _names = names if names else [None] * len(what)
            for module, name, info in zip(what, _names, tags):
                self._register(module, force=force, name=name, tags=tags)
        else:
            logger.err(
                ValueError(
                    f"Unsupported format of 'what'. Please use list or dict(tuple)."
                ),
                reraise=True,
            )

    def merge(
        self,
        others: Union["Registry", List["Registry"]],
        force: bool = False,
    ) -> None:
        if not isinstance(others, list):
            others = [others]
        if not isinstance(others[0], Registry):
            logger.err(
                TypeError("Expect `Registry` type, but got {}".format(type(others[0]))),
                reraise=True,
            )
        for other in others:
            self.register_all(other, force=force)

    @classmethod
    def find(
        cls,
        name: Optional[str] = None,
        tags: Optional[Union[str, List[str]]] = None,
        default=None,
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
                    results += [(_n, _o) for _n, _o in reg.items()]
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
            _name: obj_tag_pair[0]
            for _name, obj_tag_pair in results
            if _tags_match(tags, obj_tag_pair[1])
        }
        return results

    def __getitem__(self, __key: str) -> Any:
        return super().__getitem__(__key)[0]

    def __setitem__(self, k, v) -> None:
        assert is_pure_ansi(k), "Only ANSI chars are allowed for registering things."
        if type(v) is not tuple:
            v = (v, None)
        if len(v) != 2:
            raise ValueError("Only support value of format (object, list(str))")
        super().__setitem__(k, v)

    def __str__(self) -> str:
        return json.dumps(
            self,
            indent=4,
            ensure_ascii=False,
            sort_keys=False,
            separators=(",", ":"),
            default=str,
        )
