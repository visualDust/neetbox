# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230417

import collections
import time
from datetime import datetime
from typing import Callable, Any
from threading import Thread
from functools import partial
from neetbox.logging import logger
from neetbox.core import Registry
from neetbox.config import get_module_level_config

_watch_queue_dict = Registry("__pipeline_watch")


def __default_empty_dict():
    return {}


_listen_queue_dict = collections.defaultdict(__default_empty_dict)
__TIME_UNIT_SEC = 0.1
__TIME_CTR_MAX_CYCLE = 9999999
_update_value_dict = {}


class _WatchConfig(dict):
    def __init__(self, name, freq, initiative=False):
        self["name"] = name
        self["freq"] = freq
        self["initiative"] = initiative


class _WatchedFun:
    def __init__(self, func, others) -> None:
        self.func = func
        self.others = others

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.func(*args, **kwds)


def __get(name):
    _the_value = _update_value_dict.get(name, None)
    if _the_value and "value" in _the_value:
        _the_value = _the_value["value"]
    return _the_value


def __update_and_get(name, *args, **kwargs):
    global _update_value_dict
    _watched_fun: _WatchedFun = _watch_queue_dict[name]
    _watch_config = _watched_fun.others
    _the_value = _watched_fun(*args, **kwargs)
    _update_value_dict[name] = {
        "value": _the_value,
        "timestamp": datetime.timestamp(datetime.now()),
        "interval": (_watch_config["freq"] * __TIME_UNIT_SEC),
    }

    def _so_update_and_ping_listen(_name, _value, _watch_config):
        t0 = time.perf_counter()
        for _listener_name, _listener_func in _listen_queue_dict[_name].items():
            _listener_func(_value)
        t1 = time.perf_counter()
        delta_t = t1 - t0
        _update_freq = _watch_config["freq"]
        expected_time_limit = _update_freq * __TIME_UNIT_SEC
        if not _watch_config["initiative"] >= 0 and delta_t > expected_time_limit:
            logger.warn(
                f"Watched value {_name} takes longer time({delta_t:.8f}s) to update than it was expected({expected_time_limit}s)."
            )

    Thread(
        target=_so_update_and_ping_listen, args=(name, _the_value, _watch_config)
    ).start()
    return _the_value


def _watch(func: Callable, name: str, freq: float, initiative=False, force=False):
    """Function decorator to let the daemon watch a value of the function

    Args:
        func (function): A function returns a tuple '(name,value)'. 'name' represents the name of the value.
    """
    name = name or func.__name__
    _watch_queue_dict._register(
        name=name,
        what=_WatchedFun(
            func=func,
            others=_WatchConfig(name, freq=freq, initiative=initiative),
        ),
        force=force,
    )
    if (
        initiative
    ):  # initiatively update the value dict when the function was called manually
        logger.log(
            f"added {name} to daemon monitor. It will update on each call of the function."
        )
        return partial(__update_and_get, name)
    else:
        logger.log(
            f"added {name} to daemon monitor. It will update every {freq*__TIME_UNIT_SEC} second(s)."
        )
        return partial(__get, name)


def watch(name=None, freq=None, initiative=False, force=False):
    if not initiative:  # passively update
        freq = freq or get_module_level_config()["updateInterval"]
    else:
        freq = -1
    return partial(_watch, name=name, freq=freq, initiative=initiative, force=force)


def _listen(func: Callable, target: str, name: str = None, force=False):
    name = name or func.__name__
    if type(target) is not str:
        if type(target) is partial:
            if target.func in [__update_and_get, __get]:
                target = target.args[0]
        else:
            target = target.__name__

    if name in _listen_queue_dict[target]:
        if not force:
            logger.warn(
                f"There is already a listener called '{name}' lisiting '{target}' If you want to overwrite, try to register with 'force=True'"
            )
            return func
        else:
            logger.warn(
                f"There is already a listener called '{name}' lisiting '{target}', overwriting."
            )
    _listen_queue_dict[target][name] = func
    logger.log(f"{name} is now lisiting to {target}.")
    return func


def listen(target, name: str = None, force=False):
    return partial(_listen, target=target, name=name, force=force)


def _update_thread():
    # update values
    _ctr = 0
    while True:
        _ctr = (_ctr + 1) % __TIME_CTR_MAX_CYCLE
        time.sleep(__TIME_UNIT_SEC)
        for _vname, _watched_fun in _watch_queue_dict.items():
            _watch_config = _watched_fun.others
            if (
                not _watch_config["initiative"] and _ctr % _watch_config["freq"] == 0
            ):  # do update
                _the_value = __update_and_get(_vname)


update_thread = Thread(target=_update_thread, daemon=True)
update_thread.start()
