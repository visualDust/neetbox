# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

import os
import sys
import time
from threading import Thread
import setproctitle
from flask_socketio import SocketIO
from flask_socketio import send, emit
from flask_socketio import join_room, leave_room
from neetbox.core import Registry
from flask import Flask, abort, json, jsonify, request
from neetbox.logging import logger
from neetbox.config import get_module_level_config
from typing import Dict, Tuple

__DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC = 60 * 60 * 12  # 12 Hours
__COUNT_DOWN = __DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC
__DAEMON_NAME = "NEETBOX DAEMON"
setproctitle.setproctitle(__DAEMON_NAME)


def daemon_process(daemon_config=None):
    # getting config
    daemon_config = daemon_config or get_module_level_config()

    # describe a client
    class Client:
        connected: bool
        name: str
        status: dict = {}
        cli_ws_connection = None
        web_ws_connection = []  # client data should be able to be shown on multiple frontend

        def __init__(self, name) -> None:
            # initialize non-websocket things
            self.name = name
            pass

        def _ws_post_init(self, websocket):  # handle handshakes
            # initialize websocket things
            pass

        @staticmethod
        def from_ws(websocket):
            new_client_connection = Client()
            new_client_connection.cli_ws_connection = websocket
            new_client_connection._ws_post_init(websocket)

        def handle_ws_recv(self):
            pass

        def ws_send(self):
            pass

    # ===============================================================
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins="*")
    __client_registry = Registry("__daemon_server")  # manage connections
    connected_clients: Dict(str, Tuple(str, str)) = {}  # {sid:(name,type)} store connection only

    # ========================  WS  SERVER  ===========================

    @socketio.on("connect")
    def handle_connect():
        name = request.args.get("name")
        path = request.path
        path2type = {f"{frontend_api_root}": "web", f"{client_api_root}": "cli"}
        if not name or path not in path2type:
            # connection args not valid, drop connection
            return
        if name not in __client_registry:  # Client not found. create from websocket connection
            __client_registry._register(what=Client(name=name), name=name)
        conn_type = path2type[path]
        connected_clients[request.sid] = (
            name,
            conn_type,
        )  # store connection sid for later disconnection handling
        logger.ok(f"Websocket ({conn_type}) connected for {name} at {path}")
        # emit("connected", {"message": f"You are connected as {name}"}, room=request.sid)

    @socketio.on("disconnect")
    def handle_disconnect():
        name, conn_type = connected_clients[request.sid]
        # remove sid from Cliet entity
        if conn_type == "cli":  # remove client sid from Client
            __client_registry[name].cli_ws_connection = None
        else:
            __client_registry[name].web_ws_connection.remove(request.sid)
        logger.info(f"Websocket ({conn_type}) for {name} disconnected")

    @socketio.on("json_message")
    def handle_json_message(data):
        # TODO (visualdust) 
        name = data.get("name")
        if name in connected_clients:
            emit("forwarded_message", data, room=connected_clients[name])

    @app.route("/send_json", methods=["POST"])
    def send_json():
        # TODO (visualdust) 
        data = request.json
        name = data.get("name")
        if name in connected_clients:
            emit("forwarded_message", data, room=connected_clients[name])
            return jsonify({"message": f"Message forwarded to {name} via WebSocket"})
        return jsonify({"error": f"Client {name} is not connected"})

    # ======================== HTTP  SERVER ===========================

    frontend_api_root = "/web"
    client_api_root = "/cli"

    @app.route("/hello", methods=["GET"])
    def just_send_hello():
        return json.dumps({"hello": "hello"})

    @app.route(f"{frontend_api_root}/status/<name>", methods=["GET"])
    def return_status_of(name):
        global __COUNT_DOWN
        __COUNT_DOWN = __DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC
        if not name:
            pass  # returning full dict
        elif name in __client_registry:
            _returning_stat = __client_registry[name].status  # returning specific status
        else:
            abort(404)
        return _returning_stat

    @app.route(f"{frontend_api_root}/status/list", methods=["GET"])
    def return_names_of_status():
        global __COUNT_DOWN
        __COUNT_DOWN = __DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC
        _names = {"names": list(__client_registry.keys())}
        return _names

    @app.route(f"{client_api_root}/status/sync/<name>", methods=["POST"])
    def sync_status_of(name):  # client side function
        global __COUNT_DOWN
        __COUNT_DOWN = __DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC
        _json_data = request.get_json()
        if name not in __client_registry:  # Client not found. create from sync request
            __client_registry._register(what=Client(name=name), name=name)
        __client_registry[name].status = _json_data
        return "ok"

    @app.route(f"{frontend_api_root}/shutdown", methods=["POST"])
    def shutdown():
        global __COUNT_DOWN
        __COUNT_DOWN = -1

        def __sleep_and_shutdown(secs=3):
            time.sleep(secs)
            os._exit(0)

        Thread(target=__sleep_and_shutdown).start()  # shutdown after 3 seconds
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

    socketio.run(app, host="0.0.0.0", port=daemon_config["port"], debug=True)


if __name__ == "__main__":
    import neetbox

    cfg = get_module_level_config(neetbox.daemon.server)
    daemon_process(cfg)
