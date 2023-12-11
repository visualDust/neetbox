# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230417

import getpass
import locale
import platform
import subprocess

from neetbox.extension import on_workspace_loaded
from neetbox.utils.mvc import Singleton


class __Platform(dict, metaclass=Singleton):
    def __init__(self):
        # system
        self["username"] = getpass.getuser()
        self["machine"] = platform.machine()
        self["processor"] = "unknown" if len(platform.processor()) == 0 else platform.processor()
        self["os_name"] = platform.system()
        self["os_release"] = platform.version()
        self["architecture"] = platform.architecture()
        self["python_version"] = platform.python_version()
        self["python_build"] = platform.python_build()

    def exec(self, command):
        """
        Run a terminal command.

        Args:
            command (str): The command need to run.

        Returns:
            int: The command return code.
            str: The command running results.
            err: The command error information.
        """
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        raw_output, raw_err = p.communicate()
        rc = p.returncode
        if self.platform_info["architecture"] == "32bit":
            enc = "oem"
        else:
            enc = locale.getpreferredencoding()
        output = raw_output.decode(enc)
        err = raw_err.decode(enc)

        return rc, output.strip(), err.strip()


# watch updates in daemon
@on_workspace_loaded(name="show-platform-information")
def load_send_platform_info():
    from neetbox._daemon._protocol import (
        EVENT_TYPE_NAME_HANDSHAKE,
        EVENT_TYPE_NAME_STATUS,
        EventMsg,
    )
    from neetbox._daemon.client._client import connection

    platform = __Platform()

    @connection.ws_subscribe(event_type_name=EVENT_TYPE_NAME_HANDSHAKE)
    def ws_send_platform_info(message: EventMsg):
        connection.ws_send(
            event_type=EVENT_TYPE_NAME_STATUS, series="platform", payload=dict(platform)
        )
