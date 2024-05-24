# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231022

import functools
import json
import logging
import subprocess
import time
from collections import defaultdict
from threading import Lock, Thread
from typing import Callable

import httpx
import websocket

from neetbox._protocol import *
from neetbox.config import get_module_level_config, get_project_id, get_run_id
from neetbox.logging import Logger, RawLog
from neetbox.utils import DaemonableProcess, Registry
from neetbox.utils.massive import is_loopback
from neetbox.utils.mvc import Singleton

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


def online_only(func):
    """function decorator which checks client online status on each function call

    Args:
        func (Callable): the function

    Returns:
        Callable: the decorated function
    """

    @functools.wraps(func)
    def __online_only_func(*args, **kwargs):
        if not NeetboxClient()._is_initialized:
            with NeetboxClient()._thread_safe_lock:
                NeetboxClient()._connect_blocking()

        if NeetboxClient()._is_initialized and NeetboxClient().online_mode == False:
            return None
        return func(*args, **kwargs)

    return __online_only_func


class NeetboxClient(metaclass=Singleton):  # singleton
    online_mode: bool = None
    httpxClient: httpx.Client = httpx.Client(  # httpx client
        proxies={
            "http://": None,
            "https://": None,
        }
    )  # type: ignore
    wsApp: websocket.WebSocketApp = None  # websocket client app
    _is_initialized: bool = False
    _thread_safe_lock = Lock()
    is_ws_connected: bool = False
    ws_message_query = []  # websocket message query
    ws_subscribers = defaultdict(list)  # default to no subscribers

    @online_only
    def post_check_online(self, api: str, root: str = None, *args, **kwargs):
        url = addr_of_api(api, http_root=root)
        return self.httpxClient.post(url, *args, **kwargs)

    def post(self, api: str, root: str = None, *args, **kwargs):
        url = addr_of_api(api, http_root=root)
        return self.httpxClient.post(url, *args, **kwargs)

    @online_only
    def get_check_online(self, api: str, root: str = None, *args, **kwargs):
        url = addr_of_api(api, http_root=root)
        return self.httpxClient.get(url, *args, **kwargs)

    def get(self, api: str, root: str = None, *args, **kwargs):
        url = addr_of_api(api, http_root=root)
        return self.httpxClient.get(url, *args, **kwargs)

    @online_only
    def put_check_online(self, api: str, root: str = None, *args, **kwargs):
        url = addr_of_api(api, http_root=root)
        return self.httpxClient.put(url, *args, **kwargs)

    @online_only
    def delete_check_online(self, api: str, root: str = None, *args, **kwargs):
        url = addr_of_api(api, http_root=root)
        return self.httpxClient.delete(url, *args, **kwargs)

    def ws_subscribe(self, event_type_name: str):
        """let a function subscribe to ws messages with event type name.
        !!! dfor inner APIs only, do not use this in your code!
        !!! developers should contorl blocking on their own functions

        Args:
            function (Callable): who is subscribing the event type
            event_type_name (str, optional): Which event to listen. Defaults to None.
        """

        def _ws_subscribe(function: Callable):
            self.ws_subscribers[event_type_name].append(function)
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

    def _connect_blocking(self, config=None):
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
        self.wsApp = websocket.WebSocketApp(  # create websocket client
            url=self.ws_server_url,
            on_open=self.on_ws_open,
            on_message=self.on_ws_message,
            on_error=self.on_ws_err,
            on_close=self.on_ws_close,
        )

        Thread(
            target=self.wsApp.run_forever, kwargs={"reconnect": 1}, daemon=True
        ).start()  # initialize and start ws thread

        self._is_initialized = True

    def on_ws_open(self, ws: websocket.WebSocketApp):
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

    def on_ws_err(self, ws: websocket.WebSocketApp, msg):
        logger.err(f"client websocket encountered {msg}")

    def on_ws_close(self, ws: websocket.WebSocketApp, close_status_code, close_msg):
        logger.warn(
            f"client websocket closed: status code: {close_status_code}, message: {close_msg}"
        )
        self.is_ws_connected = False

    def on_ws_message(self, ws: websocket.WebSocketApp, message):
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
            self.is_ws_connected = True
            # return # DO NOT return!
        if message.event_type not in self.ws_subscribers:
            logger.warn(
                f"Client received a(n) {message.event_type} event but nobody subscribes it. Ignoring anyway."
            )
        for subscriber in self.ws_subscribers[message.event_type]:
            try:
                subscriber(message)  # pass payload message into subscriber
            except Exception as e:
                # subscriber throws error
                logger.err(
                    f"Subscriber {subscriber.__name__} crashed on message event {message.event_type}, ignoring."
                )

    @online_only
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
        self.ws_message_query.append(message)
        if self.is_ws_connected:  # if ws client exist
            try:
                while len(self.ws_message_query):
                    self.wsApp.send(self.ws_message_query[0].dumps())
                    self.ws_message_query.pop(0)
                return
            except Exception as e:
                pass


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


def _clean_websocket_on_exit():
    # clean websocket connection
    if connection.wsApp is not None:
        connection.wsApp.close()


import atexit

atexit.register(_clean_websocket_on_exit)
