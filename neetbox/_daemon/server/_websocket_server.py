# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20231204

from typing import Dict, Tuple

from rich import box
from rich.console import Console
from rich.table import Table

from neetbox._daemon._protocol import *

from .history import *


def get_web_socket_server(config, debug=False):
    from websocket_server import WebsocketServer

    from neetbox._daemon.server._bridge import Bridge
    from neetbox.logging import LogStyle, logger

    logger = logger("NEETBOX", LogStyle(skip_writers=["ws"]))
    console = Console()
    ws_server = WebsocketServer(host="0.0.0.0", port=config["port"] + 1)
    connected_clients: Dict(
        int, Tuple(str, IdentityType)
    ) = {}  # {cid:(name,type)} store connection only

    def handle_ws_connect(client, server):
        logger.info(f"client {client} connected. waiting for handshake...")

    def handle_ws_disconnect(client, server):
        if client["id"] not in connected_clients:
            return  # client disconnected before handshake, returning anyway
        project_id, who = connected_clients[client["id"]]
        if who == IdentityType.CLI:  # remove client from Bridge
            Bridge.of_id(project_id).cli_ws = None
        elif who == IdentityType.WEB:  # remove frontend from Bridge
            _new_web_ws_list = [
                c for c in Bridge.of_id(project_id).web_ws_list if c["id"] != client["id"]
            ]
            Bridge.of_id(project_id).web_ws_list = _new_web_ws_list
        del connected_clients[client["id"]]
        logger.info(
            f"a {who}(ws client id {client['id']}) disconnected from project '{project_id}'"
        )
        # logger.info(f"Websocket ({conn_type}) for {name} disconnected")

    def on_event_type_handshake(client, server, message: EventMsg):
        logger.debug(f"on event handshake, {message}")

        if client["id"] in connected_clients:  # client cannot handshake again
            _client_id = client["id"]
            logger.warn(
                f"websocket client(id={_client_id}) issued a duplicated handshake, ignoring..."
            )
            server.send_message(
                client=client,
                msg=EventMsg.merge(
                    message,
                    {
                        PAYLOAD_KEY: {ERROR_KEY: 400, REASON_KEY: "name not found"},
                        WHO_KEY: IdentityType.SERVER,
                    },
                ).dumps(),
            )
            return  # client cannot handshake again

        # assign this client to a Bridge

        console.log(f"handling handshake for {message.who} with project id '{message.project_id}'")
        if message.who == IdentityType.WEB:
            # new connection from frontend
            # check if Bridge with name exist
            if not Bridge.has(message.project_id):  # there is no such bridge
                server.send_message(
                    client=client,
                    msg=EventMsg.merge(
                        message,
                        {
                            PAYLOAD_KEY: {ERROR_KEY: 404, REASON_KEY: "name not found"},
                            WHO_KEY: IdentityType.SERVER,
                        },
                    ).dumps(),
                )
            else:  # assign web to bridge
                target_bridge = Bridge.of_id(message.project_id)
                target_bridge.web_ws_list.append(client)
                connected_clients[client["id"]] = (message.project_id, IdentityType.WEB)
                server.send_message(
                    client=client,
                    msg=EventMsg.merge(
                        message,
                        {
                            PAYLOAD_KEY: {RESULT_KEY: 200, REASON_KEY: "join success"},
                            WHO_KEY: IdentityType.SERVER,
                        },
                    ).dumps(),
                )
        elif message.who == IdentityType.CLI:
            # new connection from cli
            # check if Bridge with name exist
            target_bridge = Bridge(project_id=message.project_id)
            target_bridge.cli_ws = client  # assign cli to bridge
            connected_clients[client["id"]] = (message.project_id, IdentityType.CLI)
            server.send_message(
                client=client,
                msg=EventMsg.merge(
                    message,
                    {
                        PAYLOAD_KEY: {RESULT_KEY: 200, REASON_KEY: "join success"},
                        WHO_KEY: IdentityType.SERVER,
                    },
                ).dumps(),
            )
        else:
            logger.warn(f"unknown type({message.who}) of websocket trying to handshake")
        if debug:
            table = Table(
                title="Connected Websockets", box=box.MINIMAL_DOUBLE_HEAD, show_lines=True
            )
            table.add_column(PROJECT_ID_KEY, justify="center", style="magenta", no_wrap=True)
            table.add_column(WHO_KEY, justify="center", style="cyan")
            table.add_column("ws", justify="center", style="green")
            for _, _bridge in Bridge.items():
                table.add_row(_bridge.project_id, "", "")
                if _bridge.cli_ws:
                    table.add_row("", IdentityType.CLI, str(_bridge.cli_ws))
                for ws_web in _bridge.web_ws_list:
                    table.add_row("", IdentityType.WEB, str(ws_web))
            console.print(table)
        return

    def on_event_type_json(
        message: EventMsg,
        forward_to: IdentityType = IdentityType.OTHERS,
        save_history=True,
    ):
        if not Bridge.has(message.project_id):
            # project id must exist
            # drop anyway if not exist
            logger.warn(f"handle {message.event_type}. {message.project_id} not found.")
            return
        bridge = Bridge.of_id(message.project_id)
        if forward_to:
            if forward_to == IdentityType.SELF:
                forward_to = message.who
            if forward_to == IdentityType.OTHERS:
                forward_to = (
                    IdentityType.WEB if message.who == IdentityType.CLI else IdentityType.CLI
                )
            if forward_to in [IdentityType.WEB, IdentityType.BOTH]:
                bridge.ws_send_to_frontends(message)  # forward to frontends
            elif forward_to in [IdentityType.CLI, IdentityType.BOTH]:
                bridge.ws_send_to_client(message)  # forward to frontends
        if save_history:
            bridge.save_json_to_history(
                table_name=message.event_type,
                json_data=message.payload,
                series=message.series,
                run_id=message.run_id,
                timestamp=message.timestamp,
                num_row_limit=message.history_len,
            )
        return  # return after handling log forwarding

    def on_event_type_status(message: EventMsg):
        bridge = Bridge.of_id(message.project_id)
        bridge.set_status(run_id=message.run_id, series=message.series, value=message.payload)

    def on_event_type_hyperparams(message: EventMsg):
        bridge = Bridge.of_id(message.project_id)
        current_hyperparams = bridge.get_status(
            run_id=message.run_id, series=EVENT_TYPE_NAME_HPARAMS
        )[STATUS_TABLE_NAME]
        current_hyperparams[message.series] = message.payload
        message.payload = {EVENT_TYPE_NAME_HPARAMS: current_hyperparams}
        on_event_type_status(message)

    def handle_ws_message(client, server: WebsocketServer, message):
        message = EventMsg.loads(message)
        # handle event-type
        if message.event_type == EVENT_TYPE_NAME_HANDSHAKE:  # handle handshake
            on_event_type_handshake(client=client, server=server, message=message)
            return  # return after handling handshake
        if client["id"] not in connected_clients:
            return  # !!! not handling messages from cli/web without handshake. handshake is aspecial   case and should be handled anyway before this check.
        expected_identity_type = connected_clients[client["id"]][1]
        if not message.who:
            message.who = expected_identity_type
        if message.who != expected_identity_type:
            logger.warn(
                f"Illegal IdentityType: expect {expected_identity_type} but got {message.who}"
            )
            return  # !!! security check, who should match who
        else:  # handle regular event types
            if message.event_type == EVENT_TYPE_NAME_HPARAMS:
                on_event_type_hyperparams(message)
            elif message.event_type == EVENT_TYPE_NAME_STATUS:
                on_event_type_status(message)
            elif message.event_type == EVENT_TYPE_NAME_ACTION:
                on_event_type_json(
                    message=message, forward_to=IdentityType.OTHERS, save_history=False
                )
            else:
                on_event_type_json(
                    message=message,
                    forward_to=IdentityType.OTHERS,
                    save_history=True,
                )

    ws_server.set_fn_new_client(handle_ws_connect)
    ws_server.set_fn_client_left(handle_ws_disconnect)
    ws_server.set_fn_message_received(handle_ws_message)

    return ws_server
