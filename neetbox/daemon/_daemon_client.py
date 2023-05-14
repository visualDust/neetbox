# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

from neetbox.pipeline._signal_and_slot import _update_value_dict
from neetbox.logging import logger
from neetbox.config import get_module_level_config
from threading import Thread
import json
import time
from neetbox.daemon._local_http_client import _local_http_client

__TIME_UNIT_SEC = 0.1

__upload_thread: Thread = None


def _upload_thread(daemon_config, base_addr, display_name):
    _ctr = 0
    _api_name = "sync"
    _api_addr = f"{base_addr}/{_api_name}/{display_name}"
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
            resp = _local_http_client.post(_api_addr, data=_data, headers=_headers)
            if resp.is_error:
                raise IOError(f"Failed to upload data to daemon. ({resp.status_code})")
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
            logger.ok(f"Successfully reconnected to daemon.")
            _disconnect_flag = False
            _disconnect_retries = 10


def connect_daemon(daemon_config):
    _display_name = get_module_level_config()["displayName"]
    _launch_config = get_module_level_config("@")
    _display_name = _display_name or _launch_config["name"]

    logger.log(
        f"Connecting to daemon at {daemon_config['server']}:{daemon_config['port']} ..."
    )
    _daemon_address = f"{daemon_config['server']}:{daemon_config['port']}"
    base_addr = f"http://{_daemon_address}"

    # check if daemon is alive
    def _check_daemon_alive():
        _api_name = "hello"
        _api_addr = f"{base_addr}/{_api_name}"
        r = _local_http_client.get(_api_addr)
        if r.is_error:
            raise IOError(f"Daemon at {_api_addr} is not alive. ({r.status_code})")
        logger.log(f"daemon response from {_api_addr} is {r} ({r.status_code})")

    try:
        _check_daemon_alive()
    except Exception as e:
        logger.err(e)
        return False

    global __upload_thread
    if __upload_thread is None or not __upload_thread.is_alive():
        __upload_thread = Thread(
            target=_upload_thread,
            daemon=True,
            args=[daemon_config, base_addr, _display_name],
        )
        __upload_thread.start()

    return True
