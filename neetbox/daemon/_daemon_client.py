# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

from neetbox.utils import pkg
from neetbox.utils.framing import get_frame_module_traceback

module_name = get_frame_module_traceback().__name__
assert pkg.is_installed(
    "requests", try_install_if_not=True
), f"{module_name} requires requests which is not installed"
import requests
import collections
import time
import json
from datetime import datetime
from typing import Callable, Any
from threading import Thread
from functools import partial
from neetbox.config import get_module_level_config
from neetbox.logging import logger
from neetbox.core import Registry

_watch_queue_dict = Registry("__daemon_watch")


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


def listen(target: str, name: str = None, force=False):
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

                def _so_update_and_ping_listen(_vname, _watch_config):
                    t0 = time.perf_counter()
                    _the_value = __update_and_get(_vname)  # update value
                    for _listener_name, _listener_func in _listen_queue_dict[
                        _vname
                    ].items():
                        _listener_func(_the_value)
                    t1 = time.perf_counter()
                    delta_t = t1 - t0
                    _update_freq = _watch_config["freq"]
                    _update_initiative = _watch_config["initiative"]
                    expected_time_limit = _update_freq * __TIME_UNIT_SEC
                    if _update_initiative >= 0 and delta_t > expected_time_limit:
                        logger.warn(
                            f"Watched value {_vname} takes longer time({delta_t:.8f}s) to update than it was expected({expected_time_limit}s)."
                        )

                Thread(
                    target=_so_update_and_ping_listen, args=(_vname, _watch_config)
                ).start()


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
        _disconnect_flag = False
        _disconnect_retries = 10
        while True:
            _ctr = (_ctr + 1) % 99999999
            _upload_interval = daemon_config["uploadInterval"]
            time.sleep(__TIME_UNIT_SEC)
            if _ctr % _upload_interval:  # not zero
                continue
            # upload data
            _data = json.dumps(_update_value_dict, default=str)
            _headers = {"Content-Type": "application/json"}
            try:
                requests.post(_api_addr, data=_data, headers=_headers)
            except Exception as e:
                if _disconnect_flag:
                    _disconnect_retries -= 1
                    if not _disconnect_retries:
                        logger.err(
                            "Failed to reconnect to daemon after {10} retries, Trying to launch new daemon..."
                        )
                        from neetbox.daemon import _try_attach_daemon

                        _try_attach_daemon()
                        time.sleep(__TIME_UNIT_SEC)
                    continue
                logger.warn(
                    f"Failed to upload data to daemon cause {e}. Waiting for reconnect..."
                )
                _disconnect_flag = True
            else:
                if not _disconnect_flag:
                    continue
                logger.ok(f"Succefully reconnected to daemon.")
                _disconnect_flag = False
                _disconnect_retries = 10

    upload_thread = Thread(target=_upload_thread, daemon=True)
    upload_thread.start()

    return True
