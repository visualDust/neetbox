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
import time
import json
from threading import Thread
from neetbox.config import get_module_level_config
from neetbox.logging import logger
from neetbox.pipeline._signal_and_slot import _update_value_dict

__TIME_UNIT_SEC = 0.1

def connect_daemon(daemon_config):
    _display_name = get_module_level_config()["displayName"]
    _launch_config = get_module_level_config("@")
    _display_name = _display_name or _launch_config["name"]

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
