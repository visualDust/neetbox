import atexit
from threading import Thread

import httpx
import websocket
from vdtoys.framing import get_caller_info_traceback

from neetbox._protocol import *

httpxClient: httpx.Client = httpx.Client(  # httpx client
    proxies={
        "http://": None,
        "https://": None,
    }
)


class WebsocketClient:
    instances = {}

    def __init__(self, url, on_open, on_message, on_error, on_close, offline_message_buffer_size=0):
        self.wsApp = websocket.WebSocketApp(  # create websocket client
            url=url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        self.message_query = []  # websocket message query
        self.offline_message_buffer_size = offline_message_buffer_size
        self.creator = get_caller_info_traceback(stack_offset=1)
        WebsocketClient.instances[self.creator.strid] = self

    def connect(self, reconnect=1):
        if not self.wsApp:
            raise RuntimeError("You should setup WebsocketClient before connect.")
        Thread(
            target=self.wsApp.run_forever, kwargs={"reconnect": reconnect}, daemon=True
        ).start()  # initialize and start ws thread

    @property
    def is_connected(self) -> bool:
        return (
            self.wsApp.sock.connected
            if hasattr(self.wsApp, "sock") and self.wsApp.sock is not None
            else False
        )

    def send(self, message: EventMsg):
        self.message_query.append(message)
        if self.is_connected:  # if ws client exist
            try:
                while len(self.message_query):
                    self.wsApp.send(self.message_query[0].dumps())
                    self.message_query.pop(0)
            except Exception as e:
                pass
        else:
            while len(self.message_query) > self.offline_message_buffer_size:
                self.message_query.pop(0)


def _clean_websocket_on_exit():
    for client in WebsocketClient.instances.values():
        if hasattr(client, "wsApp") and client.wsApp:
            try:
                client.wsApp.close()
            except Exception as e:
                pass


# clean websocket connections on exit
atexit.register(_clean_websocket_on_exit)
