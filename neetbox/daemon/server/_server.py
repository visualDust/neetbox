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
from flask_socketio import send as ws_send
from flask_socketio import emit as ws_emit
from neetbox.core import Registry
from flask import Flask, abort, json, jsonify, request
from neetbox.logging import logger
from neetbox.config import get_module_level_config
from typing import Dict, Tuple

__DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC = 60 * 60 * 12  # 12 Hours
__COUNT_DOWN = __DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC
__DAEMON_NAME = "NEETBOX DAEMON"
setproctitle.setproctitle(__DAEMON_NAME)

FRONTEND_API_ROOT = "/web"
CLIENT_API_ROOT = "/cli"


def daemon_process(cfg=None):
    # getting config
    cfg = cfg or get_module_level_config()

    # describe a client
    class Client:
        connected: bool
        name: str
        status: dict = {}
        cli_ws_sid = None  # cli ws sid
        web_ws_sids = (
            []
        )  # frontend ws sids. client data should be able to be shown on multiple frontend

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
            new_client_connection.cli_ws_sid = websocket
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
    
    """ server behaviors when someone is requesting data of a Client 
    
    !!! some axioms
    !!! a client and related frontend(s) must connect to the server with websocket
    !!! per name, per client. No duplicate names for different client
    !!! there might be multiple frontend(s) reading from single client
    
    frontend requesting status of name 
    -   name exist: return status
    -   name not exist: return 404
    
    client synchronizing status of name
    -   name exist: update status
    -   name not exist: 
        -   create Client with name
        -   update status
    
    
    on websocket connect:
    -   its a client with name:
        -   name exist: 
            -   show warning, client websocket overwrite
            -   replace Client's ws conn sid
        -   name not exist:
            -   create Client with name (frontend may not try a ws connection before it knows the name. so not necessary to check the connection type, it must be client)
    -   its a frontend with name:
        -   name exist: add to Client's frontend ws conn list
        -   name not exist:
            -   error! frontend cannot read to a non-existing client
        
    on websocket disconnect:
    -   is a frontend conn
        -   remove sid from Client's frontend ws conn list
    -   is a client conn
        -   remove sid from Client
    -   remove from connected_clients dict
    
    on server receive json
    -    sent by client with name
        -   name exist: (name must exist)
            -   for websocket of frontend within name:
                -   forward message
    -   sent by frontend with name
        -   name exist: (name must exist)
            -   forward message to client
    """

    @socketio.on("connect")
    def handle_ws_connect():
        name = request.args.get("name")
        path = request.path
        path2type = {f"{FRONTEND_API_ROOT}": "web", f"{CLIENT_API_ROOT}": "cli"}
        if not name or path not in path2type:
            # connection args not valid, drop connection
            return
        # TODO (visualdust) check conn type for error handling
        conn_type = path2type(path)
        if name not in __client_registry:  # Client not found. create from websocket connection
            # must be cli
            client = Client(name=name)
            __client_registry._register(what=client, name=name)  # manage clients
        connected_clients[request.sid] = (
            name,
            conn_type,
        )  # store connection sid for later disconnection handling
        if conn_type == "cli":
            # add to Client
            if __client_registry[name].cli_ws_sid is not None:
                # overwriting, show warning
                logger.warn(f"cli conn with same name already exist, overwriting...")
            __client_registry[name].cli_ws_sid = request.sid
        if conn_type == "web":
            # add to Client
            __client_registry[name].web_ws_sids.append(request.sid)
        logger.ok(f"Websocket ({conn_type}) connected for {name} via {path}")

    @socketio.on("disconnect")
    def handle_ws_disconnect():
        name, conn_type = connected_clients[request.sid]
        # remove sid from Client entity
        if conn_type == "cli":  # remove client sid from Client
            __client_registry[name].cli_ws_sid = None
        else:
            __client_registry[name].web_ws_sids.remove(request.sid)
        del connected_clients[request.sid]
        logger.info(f"Websocket ({conn_type}) for {name} disconnected")

    @socketio.on("json")
    def handle_ws_json_message(data):
        name, conn_type = connected_clients[request.sid]  # who
        if conn_type == "cli":  # json data ws_send by client
            for target_sid in __client_registry[name].web_ws_sids:
                ws_send(data, to=target_sid)  # forward to every client under this name
            # no ack, not necessary to ack
        if conn_type == "web":  # json data ws_send by frontend
            cli_ws_sid = __client_registry[name].cli_ws_sid
            if cli_ws_sid is None:  # client ws disconnected:
                # ack err
                ws_send({"ack": "failed", "message": "client ws disconnected"}, to=request.sid)
                logger.warn(
                    f"frontend ({request.sid}) under name '{name}' tried to talk to a disconnected client ws."
                )
            else:  # forward to client
                target_sid = __client_registry[name].cli_ws_sid
                ws_send(data, to=target_sid)


    # ======================== HTTP  SERVER ===========================
    
    @app.route(f"{FRONTEND_API_ROOT}/wsforward/<name>", methods=["POST"])
    def handle_json_forward_to_client_ws(name): # forward frontend http json to client ws
        data = request.json
        if name in __client_registry: # client name exist
            target_sid = __client_registry[name].cli_ws_sid
            if target_sid is None: # no active cli ws connection for this name
                logger.warn(f"frontend tried to talk to forward to a disconnected client ws with name {name}.")
                abort(404) 
            ws_send(data,to=target_sid)
            return "ok"

    @app.route("/hello", methods=["GET"])
    def just_send_hello():
        return json.dumps({"hello": "hello"})

    @app.route(f"{FRONTEND_API_ROOT}/status/<name>", methods=["GET"])
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

    @app.route(f"{FRONTEND_API_ROOT}/list", methods=["GET"])
    def return_names_of_status():
        global __COUNT_DOWN
        __COUNT_DOWN = __DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC
        _names = {"names": list(__client_registry.keys())}
        return _names

    @app.route(f"{CLIENT_API_ROOT}/sync/<name>", methods=["POST"])
    def sync_status_of(name):  # client side function
        global __COUNT_DOWN
        __COUNT_DOWN = __DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC
        _json_data = request.get_json()
        if name not in __client_registry:  # Client not found. create from sync request
            __client_registry._register(what=Client(name=name), name=name)
        __client_registry[name].status = _json_data
        return "ok"

    @app.route(f"{FRONTEND_API_ROOT}/shutdown", methods=["POST"])
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

    socketio.run(app, host="0.0.0.0", port=cfg["port"], debug=True)


if __name__ == "__main__":
    import neetbox

    cfg = get_module_level_config(neetbox.daemon.server)
    daemon_process(cfg)
