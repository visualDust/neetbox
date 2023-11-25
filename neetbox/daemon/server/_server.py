# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

import os
import sys
import time
from dataclasses import dataclass
from threading import Thread
from typing import Any, Dict, Tuple

if __name__ == "__main__":
    import ultraimport  # if run server solely, sssssssuse relative import, do not trigger neetbox init

    _protocol = ultraimport("__dir__/../_protocol.py")
    from _protocol import *
else:
    from neetbox.daemon._protocol import *
import setproctitle
from flask import abort, json, request
from websocket_server import WebsocketServer

__DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC = 60 * 60 * 12  # 12 Hours
__COUNT_DOWN = __DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC
__PROC_NAME = "NEETBOX SERVER"
setproctitle.setproctitle(__PROC_NAME)


def daemon_process(cfg, debug=False):
    # describe a client
    class Bridge:
        connected: bool
        name: str
        status: dict = {}
        cli_ws = None  # cli ws sid
        web_ws_list = (
            []
        )  # frontend ws sids. client data should be able to be shown on multiple frontend

        def __init__(self, name) -> None:
            # initialize non-websocket things
            self.name = name

        def handle_ws_recv(self):
            pass

        def ws_send(self):
            pass

    # ===============================================================

    if debug:
        print("Running with debug, using APIFlask")
        from apiflask import APIFlask

        app = APIFlask(__PROC_NAME)
    else:
        print("Running in production mode, escaping APIFlask")
        from flask import Flask

        app = Flask(__PROC_NAME)

    # app = APIFlask(__PROC_NAME)

    # websocket server
    ws_server = WebsocketServer(port=cfg["port"] + 1)
    __BRIDGES = {}  # manage connections
    connected_clients: Dict(int, Tuple(str, str)) = {}  # {cid:(name,type)} store connection only

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
    -   sent by client with name
        -   name exist: (name must exist)
            -   for websocket of frontend within name:
                -   forward message
    -   sent by frontend with name
        -   name exist: (name must exist)
            -   forward message to client
    """

    def handle_ws_connect(client, server):
        print(f"client {client} connected. waiting for assigning...")

    def handle_ws_disconnect(client, server):
        _project_name, _who = connected_clients[client["id"]]
        if _who == "cli":  # remove client from Bridge
            __BRIDGES[_project_name].cli_ws = None
        else:  # remove frontend from Bridge
            _new_web_ws_list = [
                c for c in __BRIDGES[_project_name].web_ws_list if c["id"] != client["id"]
            ]
            __BRIDGES[_project_name].web_ws_list = _new_web_ws_list
        del connected_clients[client["id"]]
        print(f"a {_who} disconnected with id {client['id']}")
        # logger.info(f"Websocket ({conn_type}) for {name} disconnected")

    def handle_ws_message(client, server: WebsocketServer, message):
        message = json.loads(message)
        print(message)  # debug
        # handle event-type
        _event_type = message[EVENT_TYPE_NAME_KEY]
        _payload = message[PAYLOAD_NAME_KEY]
        _event_id = message[EVENT_ID_NAME_KEY]
        _project_name = message[NAME_NAME_KEY]
        if _event_type == "handshake":  # handle handshake
            # assign this client to a Bridge
            _who = _payload["who"]
            if _who == "web":
                # new connection from frontend
                # check if Bridge with name exist
                if _project_name not in __BRIDGES:  # there is no such bridge
                    server.send_message(
                        client=client,
                        msg=WsMsg(
                            event_type="ack",
                            event_id=_event_id,
                            payload={"result": "404", "reason": "name not found"},
                        ).json(),
                    )
                else:  # assign web to bridge
                    _target_bridge = __BRIDGES[_project_name]
                    _target_bridge.web_ws_list.append(client)
                    connected_clients[client["id"]] = (_project_name, "web")
                    server.send_message(
                        client=client,
                        msg=WsMsg(
                            event_type="ack",
                            event_id=_event_id,
                            payload={"result": "200", "reason": "join success"},
                        ).json(),
                    )
            elif _who == "cli":
                # new connection from cli
                # check if Bridge with name exist
                if _project_name not in __BRIDGES:  # there is no such bridge
                    _target_bridge = Bridge(name=_project_name)  # create new bridge for this name
                    __BRIDGES[_project_name] = _target_bridge
                __BRIDGES[_project_name].cli_ws = client  # assign cli to bridge
                connected_clients[client["id"]] = (_project_name, "web")
                server.send_message(
                    client=client,
                    msg=WsMsg(
                        name="_project_name",
                        event_type="ack",
                        event_id=_event_id,
                        payload={"result": "200", "reason": "join success"},
                    ).json(),
                )

        elif _event_type == "log":  # handle log
            # forward log to frontend
            if _project_name not in __BRIDGES:
                # project name must exist
                # drop anyway if not exist
                return
            else:
                # forward to frontends
                _target_bridge = __BRIDGES[_project_name]
                for web_ws in _target_bridge.web_ws_list:
                    server.send_message(
                        client=web_ws, msg=message
                    )  # forward original message to frontend

        elif _event_type == "action":
            # todo forward action query to cli
            pass
        elif _event_type == "ack":
            # todo forward ack to waiting acks
            pass

    ws_server.set_fn_new_client(handle_ws_connect)
    ws_server.set_fn_client_left(handle_ws_disconnect)
    ws_server.set_fn_message_received(handle_ws_message)

    # ======================== HTTP  SERVER ===========================

    # @app.route(f"{FRONTEND_API_ROOT}/wsforward/<name>", methods=["POST"])
    # def handle_json_forward_to_client_ws(name):  # forward frontend http json to client ws
    #     data = request.json
    #     if name in __BRIDGES:  # client name exist
    #         target_sid = __BRIDGES[name].cli_ws
    #         if target_sid is None:  # no active cli ws connection for this name
    #             # logger.warn(
    #             #     f"frontend tried to talk to forward to a disconnected client ws with name {name}."
    #             # )
    #             abort(404)
    #         ws_send(data, to=target_sid)
    #         return "ok"

    @app.route("/hello", methods=["GET"])
    def just_send_hello():
        return json.dumps({"hello": "hello"})

    @app.route(f"{FRONTEND_API_ROOT}/status/<name>", methods=["GET"])
    def return_status_of(name):
        global __COUNT_DOWN
        __COUNT_DOWN = __DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC
        if name in __BRIDGES:
            _returning_stat = __BRIDGES[name].status  # returning specific status
        else:
            abort(404)
        return _returning_stat

    @app.route(f"{FRONTEND_API_ROOT}/list", methods=["GET"])
    def return_names_of_status():
        global __COUNT_DOWN
        __COUNT_DOWN = __DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC
        _names = {"names": list(__BRIDGES.keys())}
        return _names

    @app.route(f"{CLIENT_API_ROOT}/sync/<name>", methods=["POST"])
    def sync_status_of(name):  # client side function
        global __COUNT_DOWN
        __COUNT_DOWN = __DAEMON_SHUTDOWN_IF_NO_UPLOAD_TIMEOUT_SEC
        _json_data = request.get_json()
        if name not in __BRIDGES:  # Client not found
            __BRIDGES[name] = Bridge(name=name)  # Create from sync request
        __BRIDGES[name].status = _json_data
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

    ws_server.run_forever(threaded=True)

    app.run(host="0.0.0.0", port=cfg["port"])


if __name__ == "__main__":
    cfg = {
        "enable": True,
        "host": "localhost",
        "port": 5000,
        "displayName": None,
        "allowIpython": False,
        "mute": True,
        "mode": "detached",
        "uploadInterval": 10,
    }
    daemon_process(cfg, debug=True)
