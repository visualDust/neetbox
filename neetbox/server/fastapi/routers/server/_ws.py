# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20240110

import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from neetbox._protocol import *
from neetbox.logging import Logger

from ._monitor import disks, hardware

router = APIRouter()

logger = Logger("Websocket.Server", skip_writers_names=["ws"])

WS_CLIENTS = []


async def handshake(websocket: WebSocket):
    await websocket.accept()
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
    # assign this client to a Bridge
    logger.info(f"handling handshake for {message.identity_type}")
    assert message.identity_type == IdentityType.WEB
    await websocket.send_json(
        data=EventMsg.merge(
            message,
            {
                PAYLOAD_KEY: {RESULT_KEY: 200, REASON_KEY: "join success"},
                IDENTITY_TYPE_KEY: IdentityType.SERVER,
            },
        ).json
    )
    WS_CLIENTS.append(websocket)
    return websocket


@router.websocket("/")
async def server_monitor_ws_endpoint(websocket: WebSocket):
    if not await handshake(websocket):
        return
    try:
        sec_counter = 0
        while True:
            await websocket.send_json(
                EventMsg(
                    project_id=None,
                    run_id=None,
                    event_type=EVENT_TYPE_NAME_HARDWARE,
                    identity_type=IdentityType.SERVER,
                    payload=hardware.json,
                    timestamp=get_timestamp(),
                ).json
            )
            time.sleep(1)
            sec_counter += 1
            if sec_counter >= 9:
                await websocket.send_json(
                    EventMsg(
                        project_id=None,
                        run_id=None,
                        event_type=EVENT_TYPE_NAME_HARDWARE,
                        identity_type=IdentityType.SERVER,
                        payload=disks.json,
                        timestamp=get_timestamp(),
                    ).json
                )
                sec_counter = 0

    except WebSocketDisconnect:
        try:
            WS_CLIENTS.remove(websocket)
        except:
            pass
