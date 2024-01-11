# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20240110

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from neetbox._protocol import *
from neetbox.logging import Logger

from ._manager import manager

router = APIRouter()
logger = Logger("WS SERVER", skip_writers_names=["ws"])


@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    ws_client = await manager.handshake(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            try:  # parse event message
                message = EventMsg.loads(message)
            except Exception as e:
                logger.err(
                    f"Illegal message format from client    {ws_client.id}: {message}, failed to parse cause {e}, dropping..."
                )
                continue
            await manager.handle_event_msg(websocket, message)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
