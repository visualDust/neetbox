import asyncio
import functools
import logging
from typing import Callable, Optional

import httpx
import websocket

from neetbox.config import get_module_level_config
from neetbox.core import Registry
from neetbox.logging import logger
from neetbox.utils.mvc import Singleton

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.ERROR)

__no_proxy = {
    "http://": None,
    "https://": None,
}

EVENT_TYPE_NAME_KEY = "event-type"
EVENT_PAYLOAD_NAME_KEY = "payload"


# singleton
class ClientConn(metaclass=Singleton):
    http: httpx.Client = None

    __ws_client: None  # _websocket_client
    __ws_subscription = Registry("__client_ws_subscription")  # { event-type-name : list(Callable)}

    def __init__(self) -> None:
        cfg = get_module_level_config()

        def __load_http_client():
            __local_http_client = httpx.Client(proxies=__no_proxy)  # type: ignore
            return __local_http_client

        # create htrtp client
        ClientConn.http = __load_http_client()
        # todo establishing socket connection

    def __on_ws_message(msg):
        logger.debug(f"ws received {msg}")
        # message should be json
        event_type_name = msg[EVENT_TYPE_NAME_KEY]
        if event_type_name not in ClientConn.__ws_subscription:
            logger.warn(
                f"Client received a(n) {event_type_name} event but nobody subscribes it. Ignoring anyway."
            )
        for subscriber in ClientConn._ws_subscribe[event_type_name]:
            try:
                subscriber(msg[EVENT_PAYLOAD_NAME_KEY])  # pass payload message into subscriber
            except Exception as e:
                # subscriber throws error
                logger.err(
                    f"Subscriber {subscriber} crashed on message event {event_type_name}, ignoring."
                )

    def ws_send(msg):
        logger.debug(f"ws sending {msg}")
        # send to ws if ws is connected, otherwise drop message? idk
        pass

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
ClientConn()  # run init
connection = ClientConn
