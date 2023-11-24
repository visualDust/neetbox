import asyncio
import functools
import logging
from dataclasses import dataclass
from threading import Thread
from typing import Any, Callable, Optional

import httpx
import websocket

from neetbox.config import get_module_level_config
from neetbox.core import Registry
from neetbox.daemon.server._server import CLIENT_API_ROOT
from neetbox.logging import logger
from neetbox.utils.mvc import Singleton

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.ERROR)

EVENT_TYPE_NAME_KEY = "event-type"
EVENT_ID_NAME_KEY = "event-id"
EVENT_PAYLOAD_NAME_KEY = "payload"


@dataclass
class WsMsg:
    event_type: str
    event_id: int = -1
    payload: Any

    def json(self):
        return {
            EVENT_TYPE_NAME_KEY: self.event_type,
            EVENT_ID_NAME_KEY: self.event_id,
            EVENT_PAYLOAD_NAME_KEY: self.payload,
        }


# singleton
class ClientConn(metaclass=Singleton):
    http: httpx.Client = None

    __ws_client: websocket.WebSocketApp = None  # _websocket_client
    __ws_subscription = Registry("__client_ws_subscription")  # { event-type-name : list(Callable)}

    def __init__(self) -> None:
        cfg = get_module_level_config()

        def __load_http_client():
            __local_http_client = httpx.Client(
                proxies={
                    "http://": None,
                    "https://": None,
                }
            )  # type: ignore
            return __local_http_client

        # create htrtp client
        ClientConn.http = __load_http_client()

    def _init_ws():
        cfg = get_module_level_config()

        # ws server url
        ClientConn.ws_server_addr = f"ws://{cfg['host']}/{CLIENT_API_ROOT}"

        # todo wait for server online
        # create websocket app
        logger.log("creating websocket connection...")
        # todo does run_forever reconnect after close?
        websocket.WebSocketApp(
            ClientConn.ws_server_addr,
            on_open=ClientConn.__on_ws_open,
            on_message=ClientConn.__on_ws_message,
            on_error=ClientConn.__on_ws_err,
            on_close=ClientConn.__on_ws_close,
        ).run_forever(reconnect=True)

        # assign self to websocket log writer
        from neetbox.logging._writer import _assign_connection_to_WebSocketLogWriter

        _assign_connection_to_WebSocketLogWriter(ClientConn)

    def __on_ws_open(ws):
        ClientConn.__ws_client = ws
        logger.ok(f"client websocket {ws} connected")

    def __on_ws_err(ws, msg):
        logger.err(f"client websocket {ws} encountered {msg}")

    def __on_ws_close(ws, close_status_code, close_msg):
        logger.warn(f"client websocket {ws} closed")
        if close_status_code or close_msg:
            logger.warn(f"ws close status code: {close_status_code}")
            logger.warn("ws close message: {close_msg}")
            ClientConn.__ws_client = None

    def __on_ws_message(ws, msg):
        """EXAMPLE JSON
        {
            "event-type": "action",
            "event-id": 111 (optional?)
            "payload": ...
        }
        """
        logger.debug(f"ws received {msg}")
        # ack to sender
        ws.send(WsMsg(event_type="ack", payload="0"))
        # message should be json
        event_type_name = msg[EVENT_TYPE_NAME_KEY]
        if event_type_name not in ClientConn.__ws_subscription:
            logger.warn(
                f"Client received a(n) {event_type_name} event but nobody subscribes it. Ignoring anyway."
            )
        for subscriber in ClientConn._ws_subscribe[event_type_name]:
            try:
                subscriber(msg)  # pass payload message into subscriber
            except Exception as e:
                # subscriber throws error
                logger.err(
                    f"Subscriber {subscriber} crashed on message event {event_type_name}, ignoring."
                )

    def ws_send(msg):
        logger.debug(f"ws sending {msg}")
        if ClientConn.__ws_client:  # if ws client exist
            ClientConn.__ws_client.send(msg)
        else:
            logger.debug("ws client not exist, message dropped.")

    def ws_subscribe(event_type_name: str):
        """let a function subscribe to ws messages with event type name.
        !!! dfor inner APIs only, do not use this in your code!
        !!! developers should contorl blocking on their own functions

        Args:
            function (Callable): who is subscribing the event type
            event_type_name (str, optional): Which event to listen. Defaults to None.
        """
        return functools.partial(ClientConn._ws_subscribe, event_type_name=event_type_name)

    def _ws_subscribe(function: Callable, event_type_name: str):
        if event_type_name not in ClientConn.__ws_subscription:
            # create subscriber list for event-type name if not exist
            ClientConn.__ws_subscription._register([], event_type_name)
        ClientConn.__ws_subscription[event_type_name].append(function)


# singleton
ClientConn()  # __init__ setup http client only
connection = ClientConn
