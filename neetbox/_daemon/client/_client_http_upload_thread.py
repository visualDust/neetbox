# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

import json

from neetbox._daemon._protocol import *
from neetbox._daemon.client._client import connection
from neetbox.client._signal_and_slot import _UPDATE_VALUE_DICT, SYSTEM_CHANNEL, watch
from neetbox.config import get_module_level_config, get_project_id
from neetbox.logging.formatting import LogStyle
from neetbox.logging.logger import Logger

logger = Logger(style=LogStyle(with_datetime=False, skip_writers=["ws"]))


def _add_upload_thread_to_watch(daemon_config, project_id):
    _api_name = "sync"
    _api = f"{CLIENT_API_ROOT}/{_api_name}/{project_id}"

    @watch(interval=daemon_config["uploadInterval"], overwrite=True, initiative=False)
    def upload_via_http():
        # dump status as json
        _data = _UPDATE_VALUE_DICT[SYSTEM_CHANNEL].copy()
        try:
            _data = json.dumps(_data, default=str)
            _headers = {"Content-Type": "application/json"}
            # upload data
            resp = connection.post(api=_api, json=_data, headers=_headers)
            if resp.is_error:  # upload failed
                raise IOError(f"Failed to upload data to daemon. ({resp.status_code})")
        except Exception as e:
            logger.warn(f"Failed to upload data to daemon cause {e}. Waiting for reconnect...")


def connect_daemon(cfg=None, launch_upload_thread=True):
    _cfg = cfg or get_module_level_config()
    logger.log(f"Connecting to daemon at {_cfg['host']}:{_cfg['port']} ...")
    _daemon_server_address = f"{_cfg['host']}:{_cfg['port']}"
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
        _add_upload_thread_to_watch(daemon_config=_cfg, project_id=get_project_id())

    connection._init_ws()
    return True
