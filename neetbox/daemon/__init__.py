# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

import json
import subprocess
import time

from neetbox.daemon.client._action_agent import _NeetActionManager as NeetActionManager
from neetbox.daemon.client._client import connection
from neetbox.daemon.client._update_thread import connect_daemon
from neetbox.daemon.server.daemonable_process import DaemonableProcess
from neetbox.logging.formatting import LogStyle
from neetbox.logging.logger import Logger

logger = Logger(style=LogStyle(with_datetime=False, skip_writers=["ws"]))


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
    _is_daemon_server_online = connect_daemon()  # try to connect daemon
    logger.debug("daemon connection status: " + str(_is_daemon_server_online))
    if not _is_daemon_server_online:  # if no daemon online
        # check if possible to launch
        if daemon_config["host"] not in ["localhost", "127.0.0.1", "0.0.0.0"]:
            # daemon not running on localhost
            logger.err(
                f"No daemon running at {daemon_config['host']}:{daemon_config['port']}, daemon will not be attached. Continue anyway."
            )
            return False

        logger.log(
            f"No daemon running at {daemon_config['host']}:{daemon_config['port']}, trying to create daemon..."
        )

        popen = DaemonableProcess(
            target="neetbox.daemon.server._daemon_launcher",
            args=["--config", json.dumps(daemon_config)],
            mode=daemon_config["mode"],
            redirect_stdout=subprocess.DEVNULL if daemon_config["mute"] else None,
            env_append={"NEETBOX_DAEMON_PROCESS": "1"},
        ).start()

        time.sleep(1)

        _retry_timeout = 10
        _time_begin = time.perf_counter()

        logger.log("Created daemon process, trying to connect to daemon...")
        while time.perf_counter() - _time_begin < 10:  # try connect daemon
            if connect_daemon():
                return True
            else:
                exit_code = popen.poll()
                if exit_code is not None:
                    logger.err(f"Daemon process exited unexpectedly with exit code {exit_code}.")
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


action = NeetActionManager.register
ws_subscribe = connection.ws_subscribe
__all__ = ["action", "ws_subscribe", "NeetActionManager", "_try_attach_daemon"]
