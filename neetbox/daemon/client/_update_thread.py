# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

import json
import time
from threading import Thread
from typing import Union

from neetbox.config import get_module_level_config
from neetbox.daemon.client._client import connection
from neetbox.daemon.server._server import CLIENT_API_ROOT
from neetbox.logging.formatting import LogStyle
from neetbox.logging.logger import Logger
from neetbox.pipeline._signal_and_slot import _UPDATE_VALUE_DICT, SYSTEM_CHANNEL, watch

logger = Logger(style=LogStyle(with_datetime=False, skip_writers=["ws"]))


def _add_upload_thread_to_watch(daemon_config, base_addr, display_name):
    _api_name = "sync"
    _api_addr = f"{base_addr}{CLIENT_API_ROOT}/{_api_name}/{display_name}"

    @watch(interval=daemon_config["uploadInterval"], overwrite=True)
    def upload_via_http():
        # dump status as json
        _data = json.dumps(_UPDATE_VALUE_DICT[SYSTEM_CHANNEL], default=str)
        _headers = {"Content-Type": "application/json"}
        try:
            # upload data
            resp = connection.http.post(_api_addr, json=_data, headers=_headers)
            if resp.is_error:  # upload failed
                raise IOError(f"Failed to upload data to daemon. ({resp.status_code})")
        except Exception as e:
            logger.warn(f"Failed to upload data to daemon cause {e}. Waiting for reconnect...")


def connect_daemon(cfg=None, launch_upload_thread=True):
    cfg = cfg or get_module_level_config()
    _display_name = get_module_level_config()["displayName"]
    _launch_config = get_module_level_config("@")
    _display_name = _display_name or _launch_config["name"]

    logger.log(f"Connecting to daemon at {cfg['host']}:{cfg['port']} ...")
    _daemon_server_address = f"{cfg['host']}:{cfg['port']}"
    _base_addr = f"http://{_daemon_server_address}"

    # check if daemon is alive
    def _check_daemon_alive(_api_addr):
        _api_name = "hello"
        _api_addr = f"{_api_addr}/{_api_name}"
        r = connection.http.get(_api_addr)
        if r.is_error:
            raise IOError(f"Daemon at {_api_addr} is not alive. ({r.status_code})")

    try:
        _check_daemon_alive(_base_addr)
        logger.ok(f"daemon alive at {_base_addr}")
    except Exception as e:
        logger.err(e)
        return False

    if launch_upload_thread:
        _add_upload_thread_to_watch(
            daemon_config=cfg, base_addr=_base_addr, display_name=_display_name
        )

    return True
