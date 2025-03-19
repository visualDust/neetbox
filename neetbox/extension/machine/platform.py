# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20230417

import getpass
import platform as _platform

from vdtoys.mvc import Singleton

from neetbox.extension import on_workspace_loaded


class PlatformInfo(metaclass=Singleton):
    def __init__(self):
        self._username = getpass.getuser()
        self._machine = _platform.machine()
        self._processor = "unknown" if len(_platform.processor()) == 0 else _platform.processor()
        self._os_name = _platform.system()
        self._os_release = _platform.version()
        self._architecture = _platform.architecture()
        self._python_version = _platform.python_version()
        self._python_build = _platform.python_build()

    @property
    def username(self):
        return self._username

    @property
    def machine(self):
        return self._machine

    @property
    def processor(self):
        return self._processor

    @property
    def os_name(self):
        return self._os_name

    @property
    def os_release(self):
        return self._os_release

    @property
    def architecture(self):
        return self._architecture

    @property
    def python_version(self):
        return self._python_version

    @property
    def python_build(self):
        return self._python_build

    @property
    def json(self):
        return {
            "username": self._username,
            "machine": self._machine,
            "processor": self._processor,
            "os_name": self._os_name,
            "os_release": self._os_release,
            "architecture": self._architecture,
            "python_version": self._python_version,
            "python_build": self._python_build,
        }

    def __str__(self) -> str:
        result = ""
        for k, v in self.json.items():
            result += f"{k}:\t{v}"
        return result


platform = PlatformInfo()


# watch updates in daemon
@on_workspace_loaded(name="show-platform-information")
def load_send_platform_info():
    from neetbox._protocol import (
        EVENT_TYPE_NAME_HANDSHAKE,
        EVENT_TYPE_NAME_STATUS,
        EventMsg,
    )
    from neetbox.client import connection

    @connection.ws_subscribe(event_type_name=EVENT_TYPE_NAME_HANDSHAKE)
    def ws_send_platform_info(message: EventMsg):
        connection.ws_send(
            event_type=EVENT_TYPE_NAME_STATUS, series="platform", payload=platform.json
        )
