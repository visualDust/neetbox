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
import time
from threading import Thread
from typing import Dict, Tuple

werkzeug_log = logging.getLogger("werkzeug")
werkzeug_log.setLevel(logging.ERROR)  # disable flask http call logs

import setproctitle
from flask import abort, json, request, send_from_directory
from websocket_server import WebsocketServer

from neetbox.daemon._protocol import *
from neetbox.history._history import *


def server_process(cfg, debug=False):
    # ===============================================================

    __PROC_NAME = "NEETBOX SERVER"
    setproctitle.setproctitle(__PROC_NAME)

    if debug:
        console.log(f"Running with debug, using APIFlask")
        from apiflask import APIFlask

        app = APIFlask(__PROC_NAME)
    else:
        console.log(f"Running in production mode, using Flask")
        from flask import Flask

        app = Flask(__PROC_NAME)

    # websocket server
    ws_server = WebsocketServer(host="0.0.0.0", port=cfg["port"] + 1)

    # describe a client
    class Bridge:
        id: str
        status: dict = {}
        cli_ws = None  # cli ws sid
        historyDB = None
        web_ws_list = (
            []
        )  # frontend ws sids. client data should be able to be shown on multiple frontend

        def set_status(self, status):
            status = json.loads(status) if isinstance(status, str) else status
            self.status = status

        def get_status(self):
            status = self.status
            status["online"] = self.cli_ws is not None
            return status

        def __init__(self, project_id) -> None:
            # initialize non-websocket things
            self.id = project_id
            self.historyDB = get_history_db(project_id=project_id)

    __BRIDGES: Dict[str, Bridge] = {}  # manage connections
    connected_clients: Dict(int, Tuple(str, str)) = {}  # {cid:(name,type)} store connection only

    def save_json_to_history(project_id, table_name, data):
        if project_id not in __BRIDGES:
            return  # todo also load not connected data from history
        __BRIDGES[project_id].historyDB.write_json(table_name=table_name, data=data)

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

    def send_to_frontends_of_id(server, project_id, message):
        if project_id not in __BRIDGES:
            if debug:
                console.log(
                    f"cannot broadcast message to frontends under name {project_id}: name not found."
                )
            return  # no such bridge
        _target_bridge = __BRIDGES[project_id]
        for web_ws in _target_bridge.web_ws_list:
            server.send_message(client=web_ws, msg=message)  # forward original message to frontend
        return

    def send_to_client_of_id(server, project_id, message):
        if project_id not in __BRIDGES:
            if debug:
                console.log(
                    f"cannot forward message to client under name {project_id}: name not found."
                )
            return  # no such bridge
        _target_bridge = __BRIDGES[project_id]
        _client = _target_bridge.cli_ws
        server.send_message(client=_client, msg=message)  # forward original message to client
        return

    def handle_ws_connect(client, server):
        console.log(f"client {client} connected. waiting for handshake...")

    def handle_ws_disconnect(client, server):
        if client["id"] not in connected_clients:
            return  # client disconnected before handshake, returning anyway
        _project_id, _who = connected_clients[client["id"]]
        if _who == "cli":  # remove client from Bridge
            __BRIDGES[_project_id].cli_ws = None
        else:  # remove frontend from Bridge
            _new_web_ws_list = [
                c for c in __BRIDGES[_project_id].web_ws_list if c["id"] != client["id"]
            ]
            __BRIDGES[_project_id].web_ws_list = _new_web_ws_list
        del connected_clients[client["id"]]
        console.log(f"a {_who} disconnected with id {client['id']}")
        # logger.info(f"Websocket ({conn_type}) for {name} disconnected")

    def on_event_type_handshake(client, server, message_dict, message):
        _payload = message_dict[PAYLOAD_NAME_KEY]
        _event_id = message_dict[EVENT_ID_NAME_KEY]
        _project_id = message_dict[WORKSPACE_ID_KEY]
        if client["id"] in connected_clients:
            # !!! cli/web could change their project name by handshake twice, this is a legal behavior
            handle_ws_disconnect(
                client=client, server=server
            )  # perform "software disconnect" before "software connect" again
        # assign this client to a Bridge
        _who = _payload["who"]
        console.log(f"handling handshake for {_who} with name {_project_id}")
        if _who == "web":
            # new connection from frontend
            # check if Bridge with name exist
            if _project_id not in __BRIDGES:  # there is no such bridge
                server.send_message(
                    client=client,
                    msg=json.dumps(
                        WsMsg(
                            project_id=_project_id,
                            event_type="handshake",
                            event_id=_event_id,
                            payload={"result": 404, "reason": "name not found"},
                        ).json()
                    ),
                )
            else:  # assign web to bridge
                _target_bridge = __BRIDGES[_project_id]
                _target_bridge.web_ws_list.append(client)
                connected_clients[client["id"]] = (_project_id, "web")
                server.send_message(
                    client=client,
                    msg=json.dumps(
                        WsMsg(
                            project_id=_project_id,
                            event_type="handshake",
                            event_id=_event_id,
                            payload={"result": 200, "reason": "join success"},
                        ).json()
                    ),
                )
        elif _who == "cli":
            # new connection from cli
            # check if Bridge with name exist
            if _project_id not in __BRIDGES:  # there is no such bridge
                _target_bridge = Bridge(project_id=_project_id)  # create new bridge for this name
                __BRIDGES[_project_id] = _target_bridge
            __BRIDGES[_project_id].cli_ws = client  # assign cli to bridge
            connected_clients[client["id"]] = (_project_id, "cli")
            server.send_message(
                client=client,
                msg=json.dumps(
                    WsMsg(
                        project_id=_project_id,
                        event_type="handshake",
                        event_id=_event_id,
                        payload={"result": 200, "reason": "join success"},
                    ).json()
                ),
            )

    def on_event_type_log(client, server, message_dict, message):
        # forward log to frontend. logs should only be sent by cli and only be received by frontends
        _project_id = message_dict[WORKSPACE_ID_KEY]
        if _project_id not in __BRIDGES:
            # project id must exist
            # drop anyway if not exist
            if debug:
                console.log(f"handle log. {_project_id} not found.")
            return
        send_to_frontends_of_id(
            server=server, project_id=_project_id, message=message
        )  # forward to frontends
        save_json_to_history(project_id=_project_id, table_name="log", data=message)
        return  # return after handling log forwarding

    def on_event_type_action(client, server, message_dict, message):
        _project_id = message_dict[WORKSPACE_ID_KEY]
        _, _who = connected_clients[client["id"]]  # check if is web or cli
        if _who == "web":  # frontend send action query to client
            send_to_client_of_id(server, _project_id, message=message)
        else:  # _who == 'cli', client send action result back to frontend(s)
            send_to_frontends_of_id(server, _project_id, message=message)
        return  # return after handling action forwarding

    def handle_ws_message(client, server: WebsocketServer, message):
        message_dict = json.loads(message)
        # handle event-type
        _event_type = message_dict[EVENT_TYPE_NAME_KEY]

        if _event_type == "handshake":  # handle handshake
            on_event_type_handshake(
                client=client, server=server, message_dict=message_dict, message=message
            )
            return  # return after handling handshake

        if client["id"] not in connected_clients:
            return  # !!! not handling messages from cli/web without handshake. handshake is a special case and should be handled anyway before this check.

        if _event_type == "log":  # handle log
            on_event_type_log(
                client=client, server=server, message_dict=message_dict, message=message
            )

        elif _event_type == "action":
            on_event_type_action(
                client=client, server=server, message_dict=message_dict, message=message
            )

        elif _event_type == "ack":
            # todo forward ack to waiting acks?
            return  # return after handling ack

    ws_server.set_fn_new_client(handle_ws_connect)
    ws_server.set_fn_client_left(handle_ws_disconnect)
    ws_server.set_fn_message_received(handle_ws_message)

    # ======================== HTTP  SERVER ===========================

    front_end_dist_path = os.path.join(os.path.dirname(__file__), "../../frontend_dist")

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

    @app.route(f"{FRONTEND_API_ROOT}/status/<project_id>", methods=["GET"])
    def return_status_of(project_id):
        if project_id in __BRIDGES:
            _returning_stat = __BRIDGES[project_id].get_status()  # returning specific status
        else:
            abort(404)
        return _returning_stat

    @app.route(f"{FRONTEND_API_ROOT}/list", methods=["GET"])
    def return_list_of_connected_project_ids():
        result = []
        for id in __BRIDGES.keys():
            result.append({"id": id, "config": __BRIDGES[id].get_status()["config"]})
        return result

    @app.route(f"{CLIENT_API_ROOT}/sync/<project_id>", methods=["POST"])
    def sync_status_of(project_id):  # client side function
        _json_data = request.get_json()
        if project_id not in __BRIDGES:  # Client not found
            __BRIDGES[project_id] = Bridge(project_id=project_id)  # Create from sync request
        __BRIDGES[project_id].set_status(_json_data)
        save_json_to_history(project_id=project_id, table_name="status", data=_json_data)
        return "ok"

    @app.route(f"{FRONTEND_API_ROOT}/shutdown", methods=["POST"])
    def shutdown():
        def __sleep_and_shutdown(secs=1):
            time.sleep(secs)
            os._exit(0)

        Thread(target=__sleep_and_shutdown).start()  # shutdown after 3 seconds
        console.log(f"BYE.")
        return f"shutdown in 1 seconds."

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
        "allowIpython": False,
        "mute": True,
        "mode": "detached",
        "uploadInterval": 10,
    }
    server_process(cfg, debug=True)
