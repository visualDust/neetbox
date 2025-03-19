# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231022

import logging
import time
from collections import defaultdict
from threading import Lock
from typing import Callable

from vdtoys.mvc import Singleton
from vdtoys.registry import Registry

from neetbox._protocol import *
from neetbox.config import get_module_level_config, get_project_id, get_run_id
from neetbox.logging import Logger, RawLog
from neetbox.utils.connection import WebsocketClient, httpxClient
from neetbox.utils.massive import is_loopback

logging.getLogger("httpx").setLevel(logging.ERROR)
logger = Logger(name_alias="CLIENT", skip_writers_names=["ws"])


def addr_of_api(api, http_root=None):
    if not http_root:
        config = get_module_level_config()
        daemon_server_address = f"{config['host']}:{config['port']}"
        http_root = f"http://{daemon_server_address}"
    if not api.startswith("/"):
        api = f"/{api}"
    result = f"{http_root}{api}"
    return result


class NeetboxClient(metaclass=Singleton):  # singleton
    def __init__(self) -> None:
        self.websocket: WebsocketClient = None
        self.online_mode: bool = None
        self._is_initialized: bool = False
        self._thread_safe_lock = Lock()
        self.subscribers = defaultdict(list)  # default to no subscribers

    @property
    def wait_should_online(self):
        with self._thread_safe_lock:
            if not self._is_initialized:
                self.initialize_connection()

        return self._is_initialized and self.online_mode is not False

    def post_check_online(self, api: str, root: str = None, *args, **kwargs):
        return (
            httpxClient.post(addr_of_api(api, http_root=root), *args, **kwargs)
            if self.wait_should_online
            else None
        )

    def post(self, api: str, root: str = None, *args, **kwargs):
        url = addr_of_api(api, http_root=root)
        return httpxClient.post(url, *args, **kwargs)

    def get_check_online(self, api: str, root: str = None, *args, **kwargs):
        return (
            httpxClient.get(addr_of_api(api, http_root=root), *args, **kwargs)
            if self.wait_should_online
            else None
        )

    def get(self, api: str, root: str = None, *args, **kwargs):
        url = addr_of_api(api, http_root=root)
        return httpxClient.get(url, *args, **kwargs)

    def put_check_online(self, api: str, root: str = None, *args, **kwargs):
        return (
            httpxClient.put(addr_of_api(api, http_root=root), *args, **kwargs)
            if self.wait_should_online
            else None
        )

    def delete_check_online(self, api: str, root: str = None, *args, **kwargs):
        return (
            httpxClient.delete(addr_of_api(api, http_root=root), *args, **kwargs)
            if self.wait_should_online
            else None
        )

    def subscribe(self, event_type_name: str, callback):
        self.subscribers[event_type_name].append(callback)  # add subscriber to list

    def unsubscribe(self, event_type_name: str, callback):
        if callback in self.subscribers[event_type_name]:
            self.subscribers[event_type_name].remove(callback)

    def ws_subscribe(self, event_type_name: str):
        """let a function subscribe to ws messages with event type name.
        !!! dfor inner APIs only, do not use this in your code!
        !!! developers should contorl blocking on their own functions

        Args:
            function (Callable): who is subscribing the event type
            event_type_name (str, optional): Which event to listen. Defaults to None.
        """

        def _ws_subscribe(function: Callable):
            self.subscribe(event_type_name, function)
            # logger.info(f"ws: {name} subscribed to '{event_type_name}'")
            return function

        return _ws_subscribe

    def check_server_connectivity(self, config=None):
        config = config or get_module_level_config()
        logger.debug(f"Connecting to daemon at {config['host']}:{config   ['port']} ...")
        daemon_server_address = f"{config['host']}:{config['port']}"
        http_root = f"http://{daemon_server_address}"

        # check if daemon is alive
        def fetch_hello(root):
            response = None
            try:
                response = self.get(api=f"{API_ROOT}/{SERVER_KEY}/hello", root=root)
                print(f"{API_ROOT}{SERIES_KEY}/hello")
                assert response.json()["hello"] == "hello"
            except:
                raise IOError(
                    f"Daemon at {root} is not alive: {response.status_code if response else 'no response'}"
                )

        try:
            fetch_hello(http_root)
            logger.ok(f"daemon alive at {http_root}")
            return True
        except Exception as e:
            logger.err(e)
            return False

    def initialize_connection(self, config=None):
        if self._is_initialized:
            return  # if already initialized, do nothing

        config = config or get_module_level_config()
        if not config["enable"]:  # check if enable
            self.online_mode = False
            self._is_initialized = True
            return

        if not config["allowIpython"]:  # check if allow ipython
            try:
                eval("__IPYTHON__")  # check if in ipython
            except NameError:  # not in ipython
                pass
            else:  # in ipython
                logger.info(
                    "NEETBOX DAEMON won't start when debugging in ipython console. If you want to allow daemon run in "
                    "ipython, try to set 'allowIpython' to True."
                )
                self.online_mode = False
                self._is_initialized = True
                return  # ignore if debugging in ipython

        server_host = config["host"]
        server_port = config["port"]
        if not self.check_server_connectivity():  # if daemon not online
            if not (
                is_loopback(server_host) or server_host in ["127.0.0.1"]
            ):  # daemon not running on localhost
                logger.err(
                    RuntimeError(
                        f"No daemon running at {server_host}:{server_port}, daemon will not be attached, stopping..."
                    ),
                    reraise=True,
                )
            # connecting localhost but no server alive, create one
            logger.log(
                f"No daemon running on {server_host}:{server_port}, trying to create daemon..."
            )
            import neetbox.server._daemon_server_launch_script as server_launcher

            popen = server_launcher.start(config)
            _retry_timeout = 10
            _time_begin = time.perf_counter()
            logger.debug("Created daemon process, trying to connect to daemon...")
            online_flag = False
            while time.perf_counter() - _time_begin < 10:  # try connect daemon
                if not self.check_server_connectivity():
                    exit_code = popen.poll()
                    if exit_code is not None:
                        logger.err(
                            f"Daemon process exited unexpectedly with exit code {exit_code}."
                        )
                        return False
                    time.sleep(0.5)
                else:
                    online_flag = True
                    break
            if not online_flag:
                logger.err(
                    RuntimeError(
                        f"Failed to connect to daemon after {_retry_timeout}s, stopping..."
                    ),
                    reraise=True,
                )

        self.online_mode = True  # enable online mode
        self.ws_server_url = f"ws://{server_host}:{server_port}{WS_ROOT}/project/"  # ws server url
        logger.info(f"websocket connecting to {self.ws_server_url}")
        self.websocket = WebsocketClient(
            url=self.ws_server_url,
            on_open=self.on_ws_open,
            on_message=self.on_ws_message,
            on_error=self.on_ws_err,
            on_close=self.on_ws_close,
            offline_message_buffer_size=100,
        )
        self.websocket.connect()
        self._is_initialized = True

    def on_ws_open(self, ws: WebsocketClient):
        project_id = get_project_id()
        logger.ok(f"client websocket connected. sending handshake as '{project_id}'...")
        handshake_msg = EventMsg(  # handshake request message
            project_id=project_id,
            run_id=get_run_id(),
            event_type=EVENT_TYPE_NAME_HANDSHAKE,
            identity_type=IdentityType.CLI,
            event_id=0,
        ).dumps()
        ws.send(handshake_msg)

    def on_ws_err(self, ws: WebsocketClient, msg):
        logger.err(f"client websocket encountered {msg}")

    def on_ws_close(self, ws: WebsocketClient, close_status_code, close_msg):
        logger.warn(
            f"client websocket closed, status code: {close_status_code}, message: {close_msg}"
        )
        self._is_initialized = False

    def on_ws_message(self, ws: WebsocketClient, message):
        message = EventMsg.loads(message)  # message should be json
        if message.event_type == EVENT_TYPE_NAME_HANDSHAKE:
            assert message.payload["result"] == 200
            logger.ok(f"neetbox handshake succeed.")
            ws.send(  # send immediately without querying
                EventMsg(
                    project_id=get_project_id(),
                    event_id=message.event_id,
                    event_type=EVENT_TYPE_NAME_STATUS,
                    series="config",
                    run_id=get_run_id(),
                    payload=get_module_level_config("@"),
                ).dumps()
            )
            # return # DO NOT return!
        if message.event_type not in self.subscribers:
            logger.warn(
                f"Client received a(n) {message.event_type} event but nobody subscribes it. Ignoring anyway."
            )
        for subscriber in self.subscribers[message.event_type]:
            try:
                subscriber(message)  # pass payload message into subscriber
            except Exception as e:
                # subscriber throws error
                logger.err(
                    f"Subscriber {subscriber.__name__} crashed on message event {message.event_type}, ignoring."
                )

    def ws_send(
        self,
        event_type: str,
        payload: dict,
        series=None,
        timestamp: str = None,
        event_id=-1,
        identity_type=IdentityType.CLI,
        _history_len=-1,
    ):
        if self.wait_should_online:
            message = EventMsg(
                project_id=get_project_id(),
                run_id=get_run_id(),
                event_type=event_type,
                event_id=event_id,
                identity_type=identity_type,
                series=series,
                payload=payload,
                timestamp=timestamp or get_timestamp(),
                history_len=_history_len,
            )

            self.websocket.send(message)


# singleton
connection = NeetboxClient()


# assign this connection to websocket log writer
LogWriters = Registry("LOG_WRITERS")


@LogWriters.register(name="ws")
def log_writer_ws(log: RawLog):
    whom = log.caller_name_alias or log.caller_info.format(r"%m > %c > %f")
    payload = {CALLER_ID_KEY: whom, MESSAGE_KEY: log.message}
    connection.ws_send(
        event_type=EVENT_TYPE_NAME_LOG,
        series=log.series,
        payload=payload,
        timestamp=log.timestamp.strftime(r"%Y-%m-%dT%H:%M:%S.%f"),
    )
