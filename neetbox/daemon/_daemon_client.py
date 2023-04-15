# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

import requests
import time
import json
from datetime import datetime
from typing import Callable, Any
from threading import Thread
from functools import partial
from neetbox.config import get_module_level_config
from neetbox.logging import logger
from neetbox.core import Registry

_update_queue_dict = Registry("daemon")
__TIME_UNIT_SEC = 0.1
__TIME_CTR_MAX_CYCLE = 9999999
_update_value_dict = {}


class _WatchConfig(dict):
    def __init__(self, name, freq, initiative=False, to_log=False):
        self["name"] = name
        self["freq"] = freq
        self["initiative"] = initiative
        self["to_log"] = to_log


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
    _watched_fun: _WatchedFun = _update_queue_dict[name]
    _watch_config = _watched_fun.others
    _the_value = _watched_fun(*args, **kwargs)
    _update_value_dict[name] = {
        "value": _the_value,
        "timestamp": datetime.timestamp(datetime.now()),
        "interval": (_watch_config["freq"] * __TIME_UNIT_SEC),
    }
    return _the_value


def _watch(func: Callable, name: str, freq: float, initiative=False, to_log=False):
    """Function decorator to let the daemon watch a value of the function

    Args:
        func (function): A function returns a tuple '(name,value)'. 'name' represents the name of the value.
    """
    name = name or func.__name__
    _update_queue_dict._register(
        name=name,
        what=_WatchedFun(
            func=func,
            others=_WatchConfig(name, freq=freq, initiative=initiative, to_log=to_log),
        ),
        force=True,
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


def watch(name=None, freq=None, initiative=False, to_log=False):
    if not initiative:  # passively update
        freq = freq or get_module_level_config()["updateInterval"]
    else:
        freq = __TIME_CTR_MAX_CYCLE + 1
    return partial(_watch, name=name, freq=freq, initiative=initiative, to_log=to_log)


def listen(name=None):
    pass  # todo


def _update_thread():
    # update values
    _ctr = 0
    while True:
        _ctr = (_ctr + 1) % __TIME_CTR_MAX_CYCLE
        time.sleep(__TIME_UNIT_SEC)
        for _vname, _watched_fun in _update_queue_dict.items():
            _watch_config = _watched_fun.others
            if (
                not _watch_config["initiative"] and _ctr % _watch_config["freq"] == 0
            ):  # do update
                _the_value = __update_and_get(_vname)


update_thread = Thread(target=_update_thread, daemon=True)
update_thread.start()


def connect_daemon(daemon_config):
    _display_name = get_module_level_config()["displayName"]
    _launch_config = get_module_level_config("@")
    _display_name = _display_name or _launch_config["name"]
    _update_value_dict = {"settings": _launch_config}

    logger.log(
        f"Connecting daemon at {daemon_config['server']}:{daemon_config['port']} ..."
    )
    _daemon_address = f"{daemon_config['server']}:{daemon_config['port']}"
    base_addr = f"http://{_daemon_address}"

    # check if daemon is alive
    def _check_daemon_alive():
        _api_name = "hello"
        _api_addr = f"{base_addr}/{_api_name}"
        r = requests.get(_api_addr)

    try:
        _check_daemon_alive()
    except Exception as e:
        return False

    def _upload_thread():
        _ctr = 0
        _api_name = "sync"
        _api_addr = f"{base_addr}/{_api_name}/{_display_name}"
        global _update_value_dict
        while True:
            _ctr = (_ctr + 1) % 99999999
            _upload_interval = daemon_config["uploadInterval"]
            time.sleep(__TIME_UNIT_SEC)
            if _ctr % _upload_interval:  # not zero
                continue
            # upload data
            _data = json.dumps(_update_value_dict, default=str)
            _headers = {"Content-Type": "application/json"}
            requests.post(_api_addr, data=_data, headers=_headers)

    upload_thread = Thread(target=_upload_thread, daemon=True)
    upload_thread.start()

    return True
