# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20231204

import json
from typing import Dict, Tuple

from rich import box
from rich.console import Console
from rich.table import Table
from websocket_server import WebsocketServer

from neetbox.daemon._protocol import *
from neetbox.daemon.server._bridge import Bridge
from neetbox.logging import LogStyle, logger

from .history import *

console = Console()
__PROC_NAME = "NEETBOX SERVER"
logger = logger(__PROC_NAME, LogStyle(skip_writers=["ws"]))


def get_web_socket_server(config, debug=False):
    ws_server = WebsocketServer(host="0.0.0.0", port=config["port"] + 1)
    connected_clients: Dict(int, Tuple(str, str)) = {}  # {cid:(name,type)} store connection only

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
        if debug:
            logger.info(f"on event handshake, {message_dict}")
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
        bridge = Bridge.of_id(project_id)
        bridge.ws_send_to_frontends(message)  # forward to frontends
        bridge.save_json_to_history(table_name="log", json_data=message)
        return  # return after handling log forwarding

    def on_event_type_action(client, server, message_dict, message):
        project_id = message_dict[PROJECT_ID_KEY]
        _, _who = connected_clients[client["id"]]  # check if is web or cli
        bridge = Bridge.of_id(project_id)
        if _who == "web":  # frontend send action query to client
            bridge.ws_send_to_client(message)
        else:  # _who == 'cli', client send action result back to frontend(s)
            bridge.ws_send_to_frontends(message=message)
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
            return  # !!! not handling messages from cli/web without handshake. handshake is aspecial   case and should be handled anyway before this check.
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

    return ws_server
