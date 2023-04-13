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
_update_value_dict = {}


def _watch(func: Callable, name: str, freq: float):
    """Function decorator to let the daemon watch a value of the function

    Args:
        func (function): A function returns a tuple '(name,value)'. 'name' represents the name of the value.
    """
    name = name or func.__name__
    _update_queue_dict[name] = (freq, func)


def watch(name=None, freq=None):
    _cfg = get_module_level_config()
    freq = freq or _cfg["updateInterval"]
    return partial(_watch, name=name, freq=freq)


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

    def _update_thread():
        # update values
        _ctr = 0
        while True:
            _ctr = (_ctr + 1) % 99999999
            time.sleep(__TIME_UNIT_SEC)
            for _vname, _vtuple in _update_queue_dict.items():
                _update_freq, _vfun = _vtuple
                if _ctr % _update_freq == 0:  # do update
                    _the_value = _vfun()
                    _update_value_dict[_vname] = {
                        "value": _the_value,
                        "timestamp": datetime.timestamp(datetime.now()),
                        "interval": (_update_freq * __TIME_UNIT_SEC),
                    }

    update_thread = Thread(target=_update_thread, daemon=True)
    update_thread.start()

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
