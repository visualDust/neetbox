# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

import os 
import sys
import time
from threading import Thread

from flask import Flask, abort, json, request

from neetbox.config import get_module_level_config
from neetbox.utils import pkg
from neetbox.utils.framing import get_frame_module_traceback

module_name = get_frame_module_traceback().__name__  # type: ignore
assert pkg.is_installed(
    "flask", try_install_if_not=True
), f"{module_name} requires flask which is not installed"

_STAT_POOL = {}
__DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC = 60 * 60 * 12  # 12 Hours
__COUNT_DOWN = __DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC
__DAEMON_NAME = "NEETBOX DAEMON"


def daemon_process(daemon_config=None):
    import setproctitle

    setproctitle.setproctitle(__DAEMON_NAME)
    daemon_config = daemon_config or get_module_level_config()
    api = Flask(__DAEMON_NAME)

    @api.route("/hello", methods=["GET"])
    def just_send_hello():
        return json.dumps({"hello": "hello"})

    @api.route("/status", methods=["GET"], defaults={"name": None})
    @api.route("/status/<name>", methods=["GET"])
    def return_status_of(name):
        global __COUNT_DOWN
        global _STAT_POOL
        __COUNT_DOWN = __DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC
        _returning_stat = dict(_STAT_POOL)
        if not name:
            pass  # returning full dict
        elif name in _returning_stat:
            _returning_stat = _returning_stat[name]  # returning specific status
        else:
            abort(404)
        return _returning_stat

    @api.route("/status/list", methods=["GET"])
    def return_names_of_status():
        global __COUNT_DOWN
        global _STAT_POOL
        __COUNT_DOWN = __DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC
        _names = {"names": list(_STAT_POOL.keys())}
        return _names

    @api.route("/sync/<name>", methods=["POST"])
    def sync_status_of(name):
        global __COUNT_DOWN
        global _STAT_POOL
        __COUNT_DOWN = __DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC
        _json_data = request.get_json()
        _STAT_POOL[name] = _json_data
        return "ok"

    @api.route("/shutdown", methods=["POST"])
    def shutdown():
        global __COUNT_DOWN
        __COUNT_DOWN = -1

        def __sleep_and_shutdown(secs=3):
            time.sleep(secs)
            os._exit(0)

        Thread(
            target=__sleep_and_shutdown
        ).start()  # shutdown after 3 seconds
        return f"shutdown in {3} seconds."

    def _count_down_thread():
        global __COUNT_DOWN
        while True:
            __COUNT_DOWN -= 1
            if not __COUNT_DOWN:
                sys.exit(0)
            time.sleep(1)

    count_down_thread = Thread(target=_count_down_thread, daemon=True)
    count_down_thread.start()

    api.run(host="0.0.0.0", port=daemon_config["port"], debug=True)

if __name__ == '__main__':
    daemon_process({
        "enable": True,
        "server": "localhost",
        "port": 20202,
        "mode": "detached",
        "displayName": None,
        "uploadInterval": 10,
        "mute": True,
        "launcher": {
            "port": 20202,
        }})