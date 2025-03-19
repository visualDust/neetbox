# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20240110

from typing import Dict
from uuid import uuid4

from fastapi import WebSocket
from rich import box
from rich.console import Console
from rich.table import Table
from vdtoys.mvc import Singleton

from neetbox._protocol import *
from neetbox.logging import Logger
from neetbox.server.fastapi.routers.project._bridge import Bridge

console = Console()
logger = Logger("Websocket.Project", skip_writers_names=["ws"])


@dataclass
class WSClient:
    id: str
    ws: WebSocket
    project_id: str
    identity_type: IdentityType
    run_id: str = None


class WSConnectionManager(metaclass=Singleton):
    id2client: Dict[str, WSClient]
    ws2client: Dict[WebSocket, WSClient]
    event_handlers: dict
    default_json_handler: dict

    def __init__(self) -> None:
        from ._event_type_handlers import (
            EVENT_TYPE_HANDLERS,
            on_event_type_default_json,
        )

        self.id2client = {}
        self.ws2client = {}
        self.event_handlers = EVENT_TYPE_HANDLERS
        self.default_json_handler = on_event_type_default_json
        logger.info(f"loaded event handlers: {list(EVENT_TYPE_HANDLERS.keys())}")

    async def handshake(self, websocket: WebSocket):
        await websocket.accept()
        id = str(uuid4())
        logger.info(f"websocket {id} connected, waiting for handshake...")
        message = await websocket.receive_text()  # the first message should be handshake message
        try:
            message = EventMsg.loads(message)
        except Exception as e:
            logger.err(f"error encountered '{e}' while handling handshake message: {message}")
            websocket.close(code=1003, reason="invalid handshake")
            return None
        assert (
            message.event_type == EVENT_TYPE_NAME_HANDSHAKE
        ), f"handshake expected but got {message.event_type}"
        assert message.project_id is not None, f"cannot handshake without project id"
        # assign this client to a Bridge
        logger.info(
            f"handling handshake for {message.identity_type}, project id '{message.project_id}'"
        )
        ws_client = WSClient(
            id=id, ws=websocket, project_id=message.project_id, identity_type=message.identity_type
        )
        if message.identity_type == IdentityType.WEB:
            if not Bridge.has(message.project_id):  # there is no such bridge
                merge_msg = {
                    PAYLOAD_KEY: {ERROR_KEY: 404, REASON_KEY: "project id not found"},
                    IDENTITY_TYPE_KEY: IdentityType.SERVER,
                }  # no such bridge, dropping...

            else:  # new connection from frontend
                bridge = Bridge.of_id(message.project_id)
                bridge.web_ws_list.append(ws_client)
                self.id2client[id] = ws_client
                self.ws2client[websocket] = ws_client
                merge_msg = {
                    PAYLOAD_KEY: {RESULT_KEY: 200, REASON_KEY: "join success"},
                    IDENTITY_TYPE_KEY: IdentityType.SERVER,
                }
        elif message.identity_type == IdentityType.CLI:
            # new connection from cli
            bridge = Bridge(project_id=message.project_id)
            run_id = message.run_id
            ws_client.run_id = run_id
            if run_id not in bridge.cli_ws_dict:
                bridge.cli_ws_dict[run_id] = ws_client  # assign cli to bridge
                self.id2client[id] = ws_client
                self.ws2client[websocket] = ws_client
                merge_msg = {
                    PAYLOAD_KEY: {RESULT_KEY: 200, REASON_KEY: "join success"},
                    IDENTITY_TYPE_KEY: IdentityType.SERVER,
                }  # handshake 200
            else:  # run id already exist
                merge_msg = {
                    PAYLOAD_KEY: {
                        ERROR_KEY: 400,
                        REASON_KEY: "client with run id already connected",
                    },
                    IDENTITY_TYPE_KEY: IdentityType.SERVER,
                }
        else:
            logger.warn(f"unknown type({message.identity_type}) of websocket trying to handshake")
            return  # unknown connection type, dropping...

        await websocket.send_json(data=EventMsg.merge(message, merge_msg).json)
        logger.ok(f"wsclient(id={id}) handshake succeed.")
        table = Table(title="Connected Websockets", box=box.MINIMAL_DOUBLE_HEAD, show_lines=True)
        table.add_column(PROJECT_ID_KEY, justify="center", style="magenta", no_wrap=True)
        table.add_column(IDENTITY_TYPE_KEY, justify="center", style="cyan")
        table.add_column(f"web:ws/cli:{RUN_ID_KEY}", justify="center", style="green")
        for _, _bridge in Bridge.items():
            table.add_row(_bridge.project_id, "", "")
            for cli_run_id, _ in _bridge.cli_ws_dict.items():
                table.add_row("", IdentityType.CLI, cli_run_id)
            for ws_web in _bridge.web_ws_list:
                table.add_row("", IdentityType.WEB, f"websocket id {ws_web.id}")
        console.print(table)
        return ws_client

    def disconnect(self, websocket: WebSocket):
        if websocket not in self.ws2client:
            return  # ignore if not handshaked
        ws_client = self.ws2client[websocket]
        id = ws_client.id
        project_id = ws_client.project_id
        identity_type = ws_client.identity_type
        bridge = Bridge.of_id(project_id)
        if not bridge:
            return  # do nothing if bridge has been deleted
        if identity_type == IdentityType.WEB:  # is web ws, remove from bridge's web ws list
            _new_web_ws_list = [c for c in Bridge.of_id(project_id).web_ws_list if c.id != id]
            bridge.web_ws_list = _new_web_ws_list
        elif (
            identity_type == IdentityType.CLI
        ):  # is cli ws, remove the run id from bridge's connected clients
            run_id = ws_client.run_id
            del bridge.cli_ws_dict[run_id]
        del self.id2client[id]
        del self.ws2client[websocket]
        logger.info(
            f"a {identity_type}(ws client id {id}) disconnected from project '{project_id}'"
        )

    async def handle_event_msg(self, websocket: WebSocket, message: EventMsg):
        ws_client = self.ws2client[websocket]
        if not message.identity_type:
            message.identity_type = ws_client.identity_type
        if message.identity_type != ws_client.identity_type:
            logger.warn(
                f"Illegal IdentityType: expect {ws_client.identity_type} but got {message.identity_type}"
            )
            return  # security check, identityType should match identityType

        # handle regular event types
        if message.event_type in self.event_handlers:
            for handler in self.event_handlers[message.event_type]:
                await handler(message)
        else:
            await self.default_json_handler(
                message=message,
                forward_to=IdentityType.OTHERS,
                save_history=True,
            )


manager = WSConnectionManager()
