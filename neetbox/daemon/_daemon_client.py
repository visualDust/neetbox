# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

import requests
import time
import json
from datetime import datetime
from typing import Callable
from threading import Thread
from functools import partial
from neetbox.config import get_module_level_config
from neetbox.logging import logger

_update_queue_dict = {}
__TIME_UNIT_SEC = 0.1
__TIME_CTR_MAX_CYCLE = 9999999
_update_value_dict = {}


def __get(name):
    _the_value = _update_value_dict.get(name, None)
    if _the_value and "value" in _the_value:
        _the_value = _the_value["value"]
    return _the_value


def __update_and_get(name):
    _vtuple = _update_queue_dict[name]
    _update_freq, _vfun = _vtuple
    _the_value = _vfun()
    _update_value_dict[name] = {
        "value": _the_value,
        "timestamp": datetime.timestamp(datetime.now()),
        "interval": (_update_freq * __TIME_UNIT_SEC),
    }
    return _the_value


def _watch(func: Callable, name: str, freq: float, initiative=False):
    """Function decorator to let the daemon watch a value of the function

    Args:
        func (function): A function returns a tuple '(name,value)'. 'name' represents the name of the value.
    """
    name = name or func.__name__
    _update_queue_dict[name] = (freq, func)
    if (
        initiative
    ):  # initiatively update the value dict when the function was called manually
        return partial(__update_and_get, name)
    else:
        return partial(__get, name)


def watch(name=None, freq=None, initiative=False):
    if not initiative:  # passively update
        freq = freq or get_module_level_config()["updateInterval"]
    else:
        freq = __TIME_CTR_MAX_CYCLE + 1
    return partial(_watch, name=name, freq=freq, initiative=initiative)


def _update_thread():
    # update values
    _ctr = 0
    while True:
        _ctr = (_ctr + 1) % __TIME_CTR_MAX_CYCLE
        time.sleep(__TIME_UNIT_SEC)
        for _vname, _vtuple in _update_queue_dict.items():
            _update_freq, _vfun = _vtuple
            if (
                _ctr % _update_freq == 0 and _update_freq <= __TIME_CTR_MAX_CYCLE
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
