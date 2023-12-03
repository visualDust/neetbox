# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

import os

import werkzeug
from rich import box
from rich.console import Console
from rich.table import Table

console = Console()
import logging
import time
from threading import Thread
from typing import Dict, Tuple

werkzeug_log = logging.getLogger("werkzeug")
werkzeug_log.setLevel(logging.ERROR)  # disable flask http call logs

import setproctitle
from flask import Response, abort, json, request, send_from_directory
from websocket_server import WebsocketServer

from neetbox.daemon._protocol import *
from neetbox.history import *
from neetbox.logging import LogStyle, logger

__PROC_NAME = "NEETBOX SERVER"
logger = logger(__PROC_NAME, LogStyle(skip_writers=["ws"]))


def server_process(cfg, debug=False):
    # ===============================================================

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
        """Bridges represent projects, running or not running, from client connection or fron history. web apis should obtain information from Bridges."""

        # static
        _id2bridge: Dict[str, "Bridge"] = {}  # manage connections using project id

        # instance vars
        project_id: str
        status: dict
        cli_ws: dict
        web_ws_list: list
        historyDB: DBConnection

        def __new__(cls, project_id: str, **kwargs) -> None:
            """Create Bridge of project id, return the old one if already exist

            Args:
                project_id (str): project id

            Returns:
                Bridge: Bridge of given project id
            """
            if project_id not in cls._id2bridge:
                new_bridge = super().__new__(cls)
                new_bridge.project_id = project_id
                new_bridge.cli_ws: dict = None  # cli ws sid
                new_bridge.web_ws_list: list = (
                    []
                )  # frontend ws sids. client data should be able to be shown on multiple frontend
                flag_auto_load_db = kwargs["auto_load_db"] if "auto_load_db" in kwargs else True
                new_bridge.historyDB = get_db_of_id(project_id) if flag_auto_load_db else None
                new_bridge.status = {}
                cls._id2bridge[project_id] = new_bridge
                logger.info(f"created new Bridge for project id '{project_id}'")
            return cls._id2bridge[project_id]

        @classmethod
        def items(cls):
            return cls._id2bridge.items()

        @classmethod
        def has(cls, project_id: str):
            return project_id in cls._id2bridge

        @classmethod
        def of_id(cls, project_id: str):
            """get Bridge of project id if exist. note that this class method is different from Bridge.__new__, which do not create new Bridge if given id not exist, it returns None instead.

            Args:
                project_id (str): project id

            Returns:
                Bridge: Bridge if id exist, otherwise None
            """
            bridge = cls._id2bridge[project_id] if cls.has(project_id) else None
            return bridge

        @classmethod
        def from_db(cls, db: DBConnection):
            project_id = db.fetch_db_project_id()
            target_bridge = Bridge(project_id, auto_load_db=False)
            if target_bridge.historyDB is not None:
                logger.warn(f"overwriting db of '{project_id}'")
            target_bridge.historyDB = db
            # put last status
            last_status = target_bridge.read_json_from_history(
                table_name="status", condition=QueryCondition(limit=1, order={"id": SortType.DESC})
            )
            if len(last_status):
                _, _, last_status = last_status[0]  # do not use set_status()
                target_bridge.status = json.loads(last_status)
            return target_bridge

        @classmethod
        def load_histories(cls):
            db_list = get_db_list()
            logger.log(f"found {len(db_list)} history db, loading...")
            for _, history_db in db_list:
                cls.from_db(history_db)

        def set_status(self, status):
            self.save_json_to_history(table_name="status", json_data=status)
            status = json.loads(status) if isinstance(status, str) else status
            self.status = status

        def get_status(self):
            status = self.status
            status["online"] = self.cli_ws is not None
            return status

        def save_json_to_history(self, table_name, json_data, series=None, timestamp=None):
            lastrowid = Bridge.of_id(self.project_id).historyDB.write_json(
                table_name=table_name, json_data=json_data, series=series, timestamp=timestamp
            )
            return lastrowid

        def read_json_from_history(self, table_name, condition):
            return self.historyDB.read_json(table_name=table_name, condition=condition)

        def save_blob_to_history(
            self, table_name, meta_data, blob_data, series=None, timestamp=None
        ):
            lastrowid = Bridge.of_id(self.project_id).historyDB.write_blob(
                table_name=table_name,
                meta_data=meta_data,
                blob_data=blob_data,
                series=series,
                timestamp=timestamp,
            )
            return lastrowid

        def read_blob_from_history(self, table_name, condition, meta_only: bool):
            return self.historyDB.read_blob(table_name, condition=condition, meta_only=meta_only)

    Bridge.load_histories()  # load history files

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

    def ws_send_to_frontends_of_id(project_id, message):
        if not Bridge.has(project_id):
            if debug:
                console.log(
                    f"cannot broadcast message to frontends under name {project_id}: name not found."
                )
            return  # no such bridge
        _target_bridge = Bridge.of_id(project_id)
        for web_ws in _target_bridge.web_ws_list:
            try:
                ws_server.send_message(
                    client=web_ws, msg=message
                )  # forward original message to frontend
            except Exception as e:
                logger.err(e)
        return

    def ws_send_to_client_of_id(project_id, message):
        if not Bridge.has(project_id):
            if debug:
                console.log(
                    f"cannot forward message to client under name {project_id}: name not found."
                )
            return  # no such bridge
        _target_bridge = Bridge.of_id(project_id)
        _client = _target_bridge.cli_ws
        try:
            ws_server.send_message(
                client=_client, msg=message
            )  # forward original message to client
        except Exception as e:
            logger.err(e)
        return

    def handle_ws_connect(client, server):
        logger.info(f"client {client} connected. waiting for handshake...")

    def handle_ws_disconnect(client, server):
        if client["id"] not in connected_clients:
            return  # client disconnected before handshake, returning anyway
        project_id, who = connected_clients[client["id"]]
        if who == "cli":  # remove client from Bridge
            Bridge.of_id(project_id).cli_ws = None
        elif who == "web":  # remove frontend from Bridge
            _new_web_ws_list = [
                c for c in Bridge.of_id(project_id).web_ws_list if c["id"] != client["id"]
            ]
            Bridge.of_id(project_id).web_ws_list = _new_web_ws_list
        del connected_clients[client["id"]]
        logger.info(
            f"a {who}(ws client id {client['id']}) disconnected from project '{project_id}'"
        )
        # logger.info(f"Websocket ({conn_type}) for {name} disconnected")

    def on_event_type_handshake(client, server, message_dict, message):
        if client["id"] in connected_clients:  # client cannot handshake again
            _client_id = client["id"]
            logger.warn(
                f"websocket client(id={_client_id}) issued a duplicated handshake, ignoring..."
            )
            server.send_message(
                client=client,
                msg=json.dumps(
                    WsMsg(
                        project_id=project_id,
                        event_type="handshake",
                        event_id=_event_id,
                        payload={"result": 400, "reason": "name not found"},
                    ).json()
                ),
            )
            return  # client cannot handshake again

        _payload = message_dict[PAYLOAD_NAME_KEY]
        _event_id = message_dict[EVENT_ID_NAME_KEY]
        project_id = message_dict[PROJECT_ID_KEY]

        # assign this client to a Bridge
        who = _payload["who"]
        console.log(f"handling handshake for {who} with project id '{project_id}'")
        if who == "web":
            # new connection from frontend
            # check if Bridge with name exist
            if not Bridge.has(project_id):  # there is no such bridge
                server.send_message(
                    client=client,
                    msg=json.dumps(
                        WsMsg(
                            project_id=project_id,
                            event_type="handshake",
                            event_id=_event_id,
                            payload={"result": 404, "reason": "name not found"},
                        ).json()
                    ),
                )
            else:  # assign web to bridge
                target_bridge = Bridge.of_id(project_id)
                target_bridge.web_ws_list.append(client)
                connected_clients[client["id"]] = (project_id, "web")
                server.send_message(
                    client=client,
                    msg=json.dumps(
                        WsMsg(
                            project_id=project_id,
                            event_type="handshake",
                            event_id=_event_id,
                            payload={"result": 200, "reason": "join success"},
                        ).json()
                    ),
                )
        elif who == "cli":
            # new connection from cli
            # check if Bridge with name exist
            target_bridge = Bridge(project_id=project_id)
            target_bridge.cli_ws = client  # assign cli to bridge
            connected_clients[client["id"]] = (project_id, "cli")
            server.send_message(
                client=client,
                msg=json.dumps(
                    WsMsg(
                        project_id=project_id,
                        event_type="handshake",
                        event_id=_event_id,
                        payload={"result": 200, "reason": "join success"},
                    ).json()
                ),
            )
        else:
            logger.warn(f"unknown type({who}) of websocket trying to handshake")
        if debug:
            table = Table(
                title="Connected Websockets", box=box.MINIMAL_DOUBLE_HEAD, show_lines=True
            )

            table.add_column("project-id", justify="center", style="magenta", no_wrap=True)
            table.add_column("who", justify="center", style="cyan")
            table.add_column("ws client", justify="center", style="green")

            for _, _bridge in Bridge.items():
                table.add_row(_bridge.project_id, "", "")
                if _bridge.cli_ws:
                    table.add_row("", "client", str(_bridge.cli_ws))
                for ws_web in _bridge.web_ws_list:
                    table.add_row("", "web", str(ws_web))

            console.print(table)
        return

    def on_event_type_log(client, server, message_dict, message):
        # forward log to frontend. logs should only be sent by cli and only be received by frontends
        project_id = message_dict[PROJECT_ID_KEY]
        if not Bridge.has(project_id):
            # project id must exist
            # drop anyway if not exist
            if debug:
                console.log(f"handle log. {project_id} not found.")
            return
        ws_send_to_frontends_of_id(project_id=project_id, message=message)  # forward to frontends
        series = message_dict[PAYLOAD_NAME_KEY]["series"]
        Bridge.of_id(project_id).save_json_to_history(
            table_name="log", json_data=message, series=series
        )
        return  # return after handling log forwarding

    def on_event_type_action(client, server, message_dict, message):
        _project_id = message_dict[PROJECT_ID_KEY]
        _, _who = connected_clients[client["id"]]  # check if is web or cli
        if _who == "web":  # frontend send action query to client
            ws_send_to_client_of_id(_project_id, message=message)
        else:  # _who == 'cli', client send action result back to frontend(s)
            ws_send_to_frontends_of_id(_project_id, message=message)
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
        return {"hello": "hello"}

    @app.route(f"{FRONTEND_API_ROOT}/list", methods=["GET"])
    def get_list_of_connected_project_ids():
        result = []
        for id, bridge in Bridge.items():
            result.append({"id": id, "config": bridge.get_status()["config"]})
        return result

    @app.route(f"{FRONTEND_API_ROOT}/status/<project_id>", methods=["GET"])
    def get_status_of(project_id):
        if not Bridge.has(project_id):
            abort(404)
        _returning_stat = Bridge.of_id(project_id).get_status()  # returning specific status
        return _returning_stat

    @app.route(f"{FRONTEND_API_ROOT}/status/<project_id>/history", methods=["GET"])
    def get_history_status_of(project_id):
        if not Bridge.has(project_id):
            abort(404)
        _json_data = request.get_json()
        try:
            condition = QueryCondition.from_json(_json_data)
        except Exception as e:  # if failed to parse
            return abort(400)
        result_list = Bridge.of_id(project_id).read_json_from_history(
            table_name="status", condition=condition
        )
        return result_list

    @app.route(f"{CLIENT_API_ROOT}/sync/<project_id>", methods=["POST"])
    def upload_status_of(project_id):  # client side function
        _json_data = request.get_json()
        target_bridge = Bridge(project_id)  # Create from sync request
        target_bridge.set_status(_json_data)
        return {"result": "ok"}

    @app.route(f"/image/<project_id>", methods=["PUT"])
    def upload_image(project_id):
        if not Bridge.has(project_id):
            # project id must exist
            # drop anyway if not exist
            if debug:
                console.log(f"handle log. {project_id} not found.")
            return abort(404)
        _json_data = request.form.to_dict()
        image_bytes = request.files["image"].read()
        lastrowid = Bridge.of_id(project_id).save_blob_to_history(
            table_name="image", meta_data=_json_data, blob_data=image_bytes
        )
        ws_send_to_frontends_of_id(
            project_id,
            json.dumps({"event-type": "image", "imageId": lastrowid, "metadata": _json_data}),
        )
        return {"result": "ok", "id": lastrowid}

    @app.route(f"{FRONTEND_API_ROOT}/image/<project_id>/<image_id>", methods=["GET"])
    def get_image_of(project_id, image_id: int):
        if not Bridge.has(project_id):
            return abort(404)  # cannot operate history if bridge of given id not exist
        meta = request.args.get("meta") is not None
        [(_, _, meta_data, image)] = Bridge.of_id(project_id).read_blob_from_history(
            table_name="image", condition=QueryCondition(id=image_id), meta_only=meta
        )

        return (
            Response(meta_data, mimetype="application/json")
            if meta
            else Response(image, mimetype="image")
        )

    @app.route(f"{FRONTEND_API_ROOT}/image/<project_id>/history", methods=["GET"])
    def get_history_image_metadata_of(project_id):
        if not Bridge.has(project_id):
            abort(404)
        _json_data = request.get_json()
        try:
            condition = QueryCondition.from_json(_json_data)
        except Exception as e:  # if failed to parse
            return abort(400)
        query_results = Bridge.of_id(project_id).read_blob_from_history(
            table_name="image", condition=condition, meta_only=True
        )  # todo ?
        result = [meta_data for _, _, meta_data, _ in query_results]
        return result

    @app.route(f"/shutdown", methods=["POST"])
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
