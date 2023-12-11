import functools
import json
import logging
import time
from collections import defaultdict
from threading import Thread
from typing import Callable

import httpx
import websocket

from neetbox._daemon._protocol import *
from neetbox.config import get_module_level_config, get_project_id, get_run_id
from neetbox.logging.formatting import LogStyle
from neetbox.logging.logger import Logger
from neetbox.utils.mvc import Singleton

logger = Logger(whom=None, style=LogStyle(skip_writers=["ws"]))

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.ERROR)

_ws_initialized = False  # indicate whether websocket has been initialized


def _load_http_client():
    __local_http_client = httpx.Client(
        proxies={
            "http://": None,
            "https://": None,
        }
    )  # type: ignore
    return __local_http_client


def addr_of_api(api, root=None):
    if not root:
        _cfg = get_module_level_config()
        _daemon_server_address = f"{_cfg['host']}:{_cfg['port']}"
        root = f"http://{_daemon_server_address}"
    if not api.startswith("/"):
        api = f"/{api}"
    return f"{root}{api}"


# singleton
class ClientConn(metaclass=Singleton):
    # http client
    http: httpx.Client = _load_http_client()

    def post(api: str, *args, **kwargs):
        url = addr_of_api(api)
        return ClientConn.http.post(url, *args, **kwargs)

    def get(api: str, *args, **kwargs):
        url = addr_of_api(api)
        return ClientConn.http.get(url, *args, **kwargs)

    def put(api: str, *args, **kwargs):
        url = addr_of_api(api)
        return ClientConn.http.put(url, *args, **kwargs)

    def delete(api: str, *args, **kwargs):
        url = addr_of_api(api)
        return ClientConn.http.delete(url, *args, **kwargs)

    __ws_client: websocket.WebSocketApp = None  # _websocket_client
    __ws_subscription = defaultdict(lambda: {})  # default to no subscribers

    def ws_subscribe(event_type_name: str, name: str = None):
        """let a function subscribe to ws messages with event type name.
        !!! dfor inner APIs only, do not use this in your code!
        !!! developers should contorl blocking on their own functions

        Args:
            function (Callable): who is subscribing the event type
            event_type_name (str, optional): Which event to listen. Defaults to None.
        """
        return functools.partial(
            ClientConn._ws_subscribe, event_type_name=event_type_name, name=name
        )

    def _ws_subscribe(function: Callable, event_type_name: str, name=None):
        name = name or function.__name__
        ClientConn.__ws_subscription[event_type_name][name] = function
        # logger.info(f"ws: {name} subscribed to '{event_type_name}'")

    @classmethod
    def _init_ws(cls):
        global _ws_initialized
        if _ws_initialized:
            return

        cfg = get_module_level_config()
        # ws server url
        cls.ws_server_addr = f"ws://{cfg['host']}:{cfg['port'] + 1}"

        # create websocket app
        logger.log(f"creating websocket connection to {cls.ws_server_addr}", skip_writers=["ws"])
        cls.wsApp = websocket.WebSocketApp(
            cls.ws_server_addr,
            on_open=cls.__on_ws_open,
            on_message=cls.__on_ws_message,
            on_error=cls.__on_ws_err,
            on_close=cls.__on_ws_close,
        )

        Thread(
            target=cls.wsApp.run_forever, kwargs={"reconnect": True}, daemon=True
        ).start()  # initialize and start ws thread

        _ws_initialized = True

    def __on_ws_open(ws: websocket.WebSocketApp):
        project_id = get_project_id()
        logger.ok(f"client websocket connected. sending handshake as '{project_id}'...")
        handshake_msg = EventMsg(  # handshake request message
            project_id=project_id,
            run_id=get_run_id(),
            event_type=EVENT_TYPE_NAME_HANDSHAKE,
            who=IdentityType.CLI,
            event_id=0,
        ).dumps()
        ws.send(handshake_msg)

    def __on_ws_err(ws: websocket.WebSocketApp, msg):
        logger.err(f"client websocket encountered {msg}")

    def __on_ws_close(ws: websocket.WebSocketApp, close_status_code, close_msg):
        logger.warn(f"client websocket closed")
        if close_status_code or close_msg:
            logger.warn(f"ws close status code: {close_status_code}")
            logger.warn("ws close message: {close_msg}")
        ClientConn.__ws_client = None

    def __on_ws_message(ws: websocket.WebSocketApp, message):
        message = EventMsg.loads(message)  # message should be json
        if message.event_type == EVENT_TYPE_NAME_HANDSHAKE:
            assert message.payload["result"] == 200
            logger.ok(f"handshake succeed.")
            ClientConn.__ws_client = ws
            ClientConn.ws_send(  # send config
                event_type=EVENT_TYPE_NAME_STATUS,
                series="config",
                payload=get_module_level_config("@"),
            )
            # return # DO NOT return!
        if message.event_type not in ClientConn.__ws_subscription:
            logger.warn(
                f"Client received a(n) {message.event_type} event but nobody subscribes it. Ignoring anyway."
            )
        for name, subscriber in ClientConn.__ws_subscription[message.event_type].items():
            try:
                subscriber(message)  # pass payload message into subscriber
            except Exception as e:
                # subscriber throws error
                logger.err(
                    f"Subscriber {name} crashed on message event {message.event_type}, ignoring."
                )

    _ws_message_query = []

    @classmethod
    def _ws_send(cls, message: EventMsg):
        cls._ws_message_query.append(message)
        if cls.__ws_client:  # if ws client exist
            while cls._ws_message_query:
                cls.__ws_client.send(cls._ws_message_query.pop(0).dumps())

    @classmethod
    def ws_send(
        cls,
        event_type: str,
        payload: dict,
        series=None,
        timestamp: str = None,
        event_id=-1,
        _history_len=-1,
    ):
        try:
            message = EventMsg(
                project_id=get_project_id(),
                run_id=get_run_id(),
                event_type=event_type,
                event_id=event_id,
                who=IdentityType.CLI,
                series=series,
                payload=payload,
                timestamp=timestamp or get_timestamp(),
                history_len=_history_len,
            )
            cls._ws_send(message=message)
        except Exception as e:
            logger.warn(f"websocket send fialed: {e}, message dropped.")


# assign this connection to websocket log writer
from neetbox.logging._writer import _assign_connection_to_WebSocketLogWriter

_assign_connection_to_WebSocketLogWriter(ClientConn)
connection = ClientConn


def check_server_connectivity(cfg=None):
    _cfg = cfg or get_module_level_config()
    logger.log(f"Connecting to daemon at {_cfg['host']}:{_cfg['port']} ...")
    _daemon_server_address = f"{_cfg['host']}:{_cfg['port']}"
    _base_addr = f"http://{_daemon_server_address}"

    # check if daemon is alive
    def _check_daemon_alive(_api_addr):
        _api_name = "hello"
        _api_addr = f"{_api_addr}/{_api_name}"
        r = connection.http.get(_api_addr)
        if r.is_error:
            raise IOError(f"Daemon at {_api_addr} is not alive. ({r.status_code})")

    try:
        _check_daemon_alive(_base_addr)
        logger.ok(f"daemon alive at {_base_addr}")
    except Exception as e:
        logger.err(e)
        return False

    connection._init_ws()
    return True
