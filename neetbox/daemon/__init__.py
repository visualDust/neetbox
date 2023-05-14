# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

from neetbox.daemon._daemon_client import connect_daemon
from neetbox.daemon.daemonable_process import DaemonableProcess
from neetbox.logging import logger
from neetbox.utils import pkg
from neetbox.pipeline import watch, listen
import subprocess
import platform
import time
import os
import json


def __attach_daemon(daemon_config):
    if not daemon_config["allowIpython"]:
        try:
            eval("__IPYTHON__")
        except NameError:
            pass
        else:
            logger.log(
                "NEETBOX DAEMON won't start when debugging in ipython console. If you want to allow daemon run in "
                "ipython, try to set 'allowIpython' to True."
            )
            return False  # ignore if debugging in ipython
    _online_status = connect_daemon(daemon_config)  # try to connect daemon
    logger.log("daemon connection status: " + str(_online_status))
    if not _online_status:  # if no daemon online
        logger.log(
            f"No daemon running at {daemon_config['server']}:{daemon_config['port']}, trying to create daemon..."
        )

        popen = DaemonableProcess(
            target="neetbox.daemon._daemon_launcher",
            args=["--config", json.dumps(daemon_config["launcher"])],
            mode=daemon_config["mode"],
            redirect_stdout=subprocess.DEVNULL if daemon_config["mute"] else None,
            env_append={"NEETBOX_DAEMON_PROCESS": "1"},
        ).start()

        time.sleep(1)

        _retry_timeout = 10
        _time_begin = time.perf_counter()

        logger.log("Created daemon process, trying to connect to daemon...")
        while time.perf_counter() - _time_begin < 10:  # try connect daemon
            if connect_daemon(daemon_config):
                return True
            else:
                exit_code = popen.poll()
                if exit_code is not None:
                    logger.err(
                        f"Daemon process exited unexpectedly with exit code {exit_code}."
                    )
                    return False

                time.sleep(0.5)

        logger.err(
            f"Failed to connect to daemon after {_retry_timeout}s, daemon connector won't start."
        )
        return False


def _try_attach_daemon():
    from neetbox.config import get_module_level_config

    _cfg = get_module_level_config()
    if _cfg["enable"]:
        __attach_daemon(_cfg)


__all__ = ["watch", "listen", "_try_attach_daemon"]
