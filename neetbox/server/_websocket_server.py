# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231204

from typing import Dict, Tuple

from rich import box
from rich.console import Console
from rich.table import Table

from neetbox._protocol import *


def get_web_socket_server(config, debug=False):
    from websocket_server import WebsocketServer

    from neetbox.logging import LogStyle
    from neetbox.logging.logger import Logger, LogLevel
    from neetbox.server._bridge import Bridge

    console = Console()
    logger = Logger("NEETBOX", LogStyle(skip_writers=["ws"]))
    if debug:
        logger.set_log_level(LogLevel.DEBUG)

    port = config["port"] + 1
    logger.info(f"creating web socket server on port {port}")
    ws_server = WebsocketServer(host="0.0.0.0", port=port)
    connected_clients: Dict(
        int, Tuple(str, str, IdentityType)
    ) = {}  # {cid:(project_id, run_id,type)} store connection only

    def who_is(client):
        if client["id"] not in connected_clients:
            raise RuntimeError(
                f"Could not determine who is {client}, it seems that this client has not done handshake."
            )
        project_id, run_id, identity_type = connected_clients[client["id"]]
        return project_id, run_id, identity_type

    def handle_ws_connect(client, server):
        logger.info(
            f"client(id={client['id']}) on {client['address']} connected. waiting for handshake..."
        )
        # do nothing before handshake message

    def handle_ws_disconnect(client, server):
        ws_client_id = client["id"]
        if ws_client_id not in connected_clients:
            return  # client disconnected before handshake, returning anyway
        project_id, run_id, who = connected_clients[ws_client_id]
        bridge = Bridge.of_id(project_id)
        if not bridge:
            return  # do nothing if bridge has been deleted
        if who == IdentityType.WEB:  # is web ws, remove from bridge's web ws list
            _new_web_ws_list = [
                c for c in Bridge.of_id(project_id).web_ws_list if c["id"] != ws_client_id
            ]
            bridge.web_ws_list = _new_web_ws_list
        elif (
            who == IdentityType.CLI
        ):  # is cli ws, remove the run id from bridge's connected clients
            del bridge.cli_ws_dict[run_id]
        del connected_clients[ws_client_id]  # remove from connected clients records
        logger.info(
            f"a {who}(ws client id {ws_client_id}) disconnected from project '{project_id}'"
        )

    def on_event_type_handshake(client, server, message: EventMsg):
        ws_client_id = client["id"]
        if ws_client_id in connected_clients:  # client cannot handshake again
            logger.warn(
                f"websocket client(id={ws_client_id}) issued a duplicated handshake, ignoring..."
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
            if not Bridge.has(message.project_id):  # there is no such bridge
                merge_msg = {
                    PAYLOAD_KEY: {ERROR_KEY: 404, REASON_KEY: "project id not found"},
                    WHO_KEY: IdentityType.SERVER,
                }  # no such bridge, dropping...

            else:  # new connection from frontend
                bridge = Bridge.of_id(message.project_id)
                bridge.web_ws_list.append(client)
                connected_clients[ws_client_id] = (
                    message.project_id,
                    None,
                    IdentityType.WEB,
                )  # web have None run id
                merge_msg = {
                    PAYLOAD_KEY: {RESULT_KEY: 200, REASON_KEY: "join success"},
                    WHO_KEY: IdentityType.SERVER,
                }
        elif message.who == IdentityType.CLI:
            # new connection from cli
            bridge = Bridge(project_id=message.project_id)
            target_run_id = message.run_id
            if target_run_id not in bridge.cli_ws_dict:
                bridge.cli_ws_dict[target_run_id] = client  # assign cli to bridge
                connected_clients[ws_client_id] = (
                    message.project_id,
                    message.run_id,
                    IdentityType.CLI,
                )
                merge_msg = {
                    PAYLOAD_KEY: {RESULT_KEY: 200, REASON_KEY: "join success"},
                    WHO_KEY: IdentityType.SERVER,
                }  # handshake 200
            else:  # run id already exist
                merge_msg = {
                    PAYLOAD_KEY: {
                        ERROR_KEY: 400,
                        REASON_KEY: "client with run id already connected",
                    },
                    WHO_KEY: IdentityType.SERVER,
                }
        else:
            logger.warn(f"unknown type({message.who}) of websocket trying to handshake")
            return  # unknown connection type, dropping...

        server.send_message(  # send handshake feedback to the client
            client=client,
            msg=EventMsg.merge(message, merge_msg).dumps(),
        )

        logger.ok(f"client(id={client['id']}) on {client['address']} handshake succeed.")

        if debug:
            table = Table(
                title="Connected Websockets", box=box.MINIMAL_DOUBLE_HEAD, show_lines=True
            )
            table.add_column(PROJECT_ID_KEY, justify="center", style="magenta", no_wrap=True)
            table.add_column(WHO_KEY, justify="center", style="cyan")
            table.add_column(f"web:ws/cli:{RUN_ID_KEY}", justify="center", style="green")
            for _, _bridge in Bridge.items():
                table.add_row(_bridge.project_id, "", "")
                for cli_run_id, _ in _bridge.cli_ws_dict.items():
                    table.add_row("", IdentityType.CLI, cli_run_id)
                for ws_web in _bridge.web_ws_list:
                    table.add_row(
                        "", IdentityType.WEB, f"websocket id {ws_web['id']} on {ws_web['address']}"
                    )
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
        if save_history:
            message.id = bridge.save_json_to_history(
                table_name=message.event_type,
                json_data=message.payload,
                series=message.series,
                run_id=message.run_id,
                timestamp=message.timestamp,
                num_row_limit=message.history_len,
            )
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
                bridge.ws_send_to_client(message, run_id=message.run_id)  # forward to frontends

        return  # return after handling log forwarding

    def on_event_type_status(message: EventMsg):
        bridge = Bridge.of_id(message.project_id)
        bridge.set_status(run_id=message.run_id, series=message.series, value=message.payload)

    def on_event_type_hyperparams(message: EventMsg):
        bridge = Bridge.of_id(message.project_id)
        current_hyperparams = bridge.get_status(
            run_id=message.run_id, series=EVENT_TYPE_NAME_HPARAMS
        )  # get hyper params from status
        if message.series:  # if series of hyperparams specified
            current_hyperparams[message.series] = message.payload
        else:
            for k, v in message.payload.items():
                current_hyperparams[k] = v
        bridge.set_status(
            run_id=message.run_id, series=EVENT_TYPE_NAME_HPARAMS, value=current_hyperparams
        )

    def handle_ws_message(client, server: WebsocketServer, message):
        try:
            message = EventMsg.loads(message)
        except Exception as e:
            logger.err(
                f"Illegal message format from client {client}: {message}, failed to parse cause {e}, dropping..."
            )
            return
        # handle event-type
        if message.event_type == EVENT_TYPE_NAME_HANDSHAKE:  # handle handshake
            on_event_type_handshake(client=client, server=server, message=message)
            return  # return after handling handshake
        try:
            _, _, identity_type = who_is(client)
        except:
            logger.debug(f"ws sending message without handshake, dropping...")
            return  # !!! not handling messages from cli/web without handshake. handshake is aspecial   case and should be handled anyway before this check.
        if not message.who:
            message.who = identity_type
        if message.who != identity_type:
            logger.warn(f"Illegal IdentityType: expect {identity_type} but got {message.who}")
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
