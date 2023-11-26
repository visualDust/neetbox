# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230417

import getpass
import locale
import platform
import subprocess

from neetbox.config import get_module_level_config
from neetbox.integrations import call_on_workspace_load
from neetbox.pipeline import watch
from neetbox.pipeline._signal_and_slot import SYSTEM_CHANNEL
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


# singleton
platform = __Platform()


# watch updates in daemon
@call_on_workspace_load(name="show-platform-information")
def load_monit_hardware():
    cfg = get_module_level_config()
    if cfg["monit"]:  # if do monit hardware
        # watch updates in daemon
        @watch(name="platform", initiative=True, _channel=SYSTEM_CHANNEL)
        def update_env_stat():
            return dict(platform)

        update_env_stat()  # call once
