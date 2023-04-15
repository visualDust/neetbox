# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

from neetbox.utils import pkg
from neetbox.config import get_module_level_config
from threading import Thread
import time
import sys

_STAT_POOL = {}
__DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC = 60 * 60
__COUNT_DOWN = __DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC
__DAEMON_NAME = "NEETBOX DAEMON"


def daemon_process(daemon_config=None):
    import setproctitle

    setproctitle.setproctitle(__DAEMON_NAME)
    daemon_config = daemon_config or get_module_level_config()
    from flask import Flask, json, abort, request
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
            pass
        elif name in _returning_stat:
            _returning_stat = _returning_stat[name]
        else:
            abort(404)
        return _returning_stat

    @api.route("/sync/<name>", methods=["POST"])
    def sync_status_of(name):
        global __COUNT_DOWN
        global _STAT_POOL
        __COUNT_DOWN = __DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC
        _json_data = request.get_json()
        _STAT_POOL[name] = _json_data
        return "ok"

    def _count_down_thread():
        global __COUNT_DOWN
        while True:
            __COUNT_DOWN -= 1
            if not __COUNT_DOWN:
                sys.exit(0)
            time.sleep(1)

    count_down_thread = Thread(target=_count_down_thread, daemon=True)
    count_down_thread.start()

    api.run(host="0.0.0.0", port=daemon_config["port"])
