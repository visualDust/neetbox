# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

import os

import werkzeug
from rich.console import Console

console = Console()
import logging
import sys
import time
from dataclasses import dataclass
from threading import Thread
from typing import Any, Dict, Tuple

werkzeug_log = logging.getLogger("werkzeug")
werkzeug_log.setLevel(logging.ERROR)  # disable flask http call logs

if __name__ == "__main__":
    import ultraimport  # if run server solely, sssssssuse relative import, do not trigger neetbox init

    _protocol = ultraimport("__dir__/../_protocol.py")
    from _protocol import *
else:
    from neetbox.daemon._protocol import *

import setproctitle
from flask import abort, json, request, send_from_directory
from websocket_server import WebsocketServer

__PROC_NAME = "NEETBOX SERVER"
setproctitle.setproctitle(__PROC_NAME)


def server_process(cfg, debug=False):
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

    print()
    if debug:
        console.log(f"Running with debug, using APIFlask")
        from apiflask import APIFlask

        app = APIFlask(__PROC_NAME)
    else:
        console.log(f"Running in production mode, using Flask")
        from flask import Flask

        app = Flask(__PROC_NAME)

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
        console.log(f"client {client} connected. waiting for handshake...")

    def handle_ws_disconnect(client, server):
        if client["id"] not in connected_clients:
            return  # client disconnected before handshake, returning anyway
        _project_name, _who = connected_clients[client["id"]]
        if _who == "cli":  # remove client from Bridge
            __BRIDGES[_project_name].cli_ws = None
        else:  # remove frontend from Bridge
            _new_web_ws_list = [
                c for c in __BRIDGES[_project_name].web_ws_list if c["id"] != client["id"]
            ]
            __BRIDGES[_project_name].web_ws_list = _new_web_ws_list
        del connected_clients[client["id"]]
        console.log(f"a {_who} disconnected with id {client['id']}")
        # logger.info(f"Websocket ({conn_type}) for {name} disconnected")

    def handle_ws_message(client, server: WebsocketServer, message):
        message_dict = json.loads(message)
        # handle event-type
        _event_type = message_dict[EVENT_TYPE_NAME_KEY]
        _payload = message_dict[PAYLOAD_NAME_KEY]
        _event_id = message_dict[EVENT_ID_NAME_KEY]
        _project_name = message_dict[NAME_NAME_KEY]
        if _event_type == "handshake":  # handle handshake
            if client["id"] in connected_clients:
                # !!! cli/web could change their project name by handshake twice, this is a legal behavior
                handle_ws_disconnect(
                    client=client, server=server
                )  # perform "software disconnect" before "software connect" again
            # assign this client to a Bridge
            _who = _payload["who"]
            console.log(f"handling handshake for {_who} with name {_project_name}")
            if _who == "web":
                # new connection from frontend
                # check if Bridge with name exist
                if _project_name not in __BRIDGES:  # there is no such bridge
                    server.send_message(
                        client=client,
                        msg=json.dumps(
                            WsMsg(
                                name=_project_name,
                                event_type="handshake",
                                event_id=_event_id,
                                payload={"result": 404, "reason": "name not found"},
                            ).json()
                        ),
                    )
                else:  # assign web to bridge
                    _target_bridge = __BRIDGES[_project_name]
                    _target_bridge.web_ws_list.append(client)
                    connected_clients[client["id"]] = (_project_name, "web")
                    server.send_message(
                        client=client,
                        msg=json.dumps(
                            WsMsg(
                                name=_project_name,
                                event_type="handshake",
                                event_id=_event_id,
                                payload={"result": 200, "reason": "join success"},
                            ).json()
                        ),
                    )
            elif _who == "cli":
                # new connection from cli
                # check if Bridge with name exist
                if _project_name not in __BRIDGES:  # there is no such bridge
                    _target_bridge = Bridge(name=_project_name)  # create new bridge for this name
                    __BRIDGES[_project_name] = _target_bridge
                __BRIDGES[_project_name].cli_ws = client  # assign cli to bridge
                connected_clients[client["id"]] = (_project_name, "cli")
                server.send_message(
                    client=client,
                    msg=json.dumps(
                        WsMsg(
                            name=_project_name,
                            event_type="handshake",
                            event_id=_event_id,
                            payload={"result": 200, "reason": "join success"},
                        ).json()
                    ),
                )
            return  # return after handling handshake

        if client["id"] not in connected_clients:
            return  # !!! not handling messages from cli/web without handshake. handshake is a special case and should be handled anyway before this check.

        _, _who = connected_clients[client["id"]]  # check if is web or cli

        def send_to_frontends_of_name(name, message):
            if name not in __BRIDGES:
                if debug:
                    console.log(
                        f"cannot broadcast message to frontends under name {name}: name not found."
                    )
                return  # no such bridge
            _target_bridge = __BRIDGES[name]
            for web_ws in _target_bridge.web_ws_list:
                server.send_message(
                    client=web_ws, msg=message
                )  # forward original message to frontend
            return

        def send_to_client_of_name(name, message):
            if name not in __BRIDGES:
                if debug:
                    console.log(
                        f"cannot forward message to client under name {name}: name not found."
                    )
                return  # no such bridge
            _target_bridge = __BRIDGES[name]
            _client = _target_bridge.cli_ws
            server.send_message(client=_client, msg=message)  # forward original message to client
            return

        if _event_type == "log":  # handle log
            # forward log to frontend. logs should only be sent by cli and only be received by frontends
            if _project_name not in __BRIDGES:
                # project name must exist
                # drop anyway if not exist
                if debug:
                    console.log(f"handle log. {_project_name} not found.")
                return
            else:
                send_to_frontends_of_name(
                    name=_project_name, message=message
                )  # forward to frontends
            return  # return after handling log forwarding

        if _event_type == "action":
            if _who == "web":  # frontend send action query to client
                send_to_client_of_name(_project_name, message=message)
            else:  # _who == 'cli', client send action result back to frontend(s)
                send_to_frontends_of_name(_project_name, message=message)
            return  # return after handling action forwarding

        if _event_type == "ack":
            # todo forward ack to waiting acks
            return  # return after handling ack

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

    front_end_dist_path = os.path.join(os.path.dirname(__file__), "../../frontend/dist")

    @app.route("/")
    def static_serve_root():
        return send_from_directory(front_end_dist_path, "index.html")

    @app.route("/<path:name>")
    def static_serve(name):
        try:
            return send_from_directory(front_end_dist_path, name)
        except werkzeug.exceptions.NotFound:
            return send_from_directory(front_end_dist_path, "index.html")

    @app.route("/hello", methods=["GET"])
    def just_send_hello():
        return json.dumps({"hello": "hello"})

    @app.route(f"{FRONTEND_API_ROOT}/status/<name>", methods=["GET"])
    def return_status_of(name):
        if name in __BRIDGES:
            _returning_stat = __BRIDGES[name].status  # returning specific status
        else:
            abort(404)
        return _returning_stat

    @app.route(f"{FRONTEND_API_ROOT}/list", methods=["GET"])
    def return_names_of_status():
        _names = {"names": list(__BRIDGES.keys())}
        return _names

    @app.route(f"{CLIENT_API_ROOT}/sync/<name>", methods=["POST"])
    def sync_status_of(name):  # client side function
        print("on sync")
        _json_data = request.get_json()
        if name not in __BRIDGES:  # Client not found
            __BRIDGES[name] = Bridge(name=name)  # Create from sync request
        __BRIDGES[name].status = _json_data
        print("on done")

        return "ok"

    @app.route(f"{FRONTEND_API_ROOT}/shutdown", methods=["POST"])
    def shutdown():
        def __sleep_and_shutdown(secs=3):
            time.sleep(secs)
            os._exit(0)

        Thread(target=__sleep_and_shutdown).start()  # shutdown after 3 seconds
        console.log(f"BYE.")
        return f"shutdown in {3} seconds."

    console.log(f"launching websocket server...")
    ws_server.run_forever(threaded=True)

    _port = cfg["port"]
    console.log(f"visit server at http://localhost:{_port}")
    app.run(host="0.0.0.0", port=_port)


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
    server_process(cfg, debug=True)
