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
    logger.log('daemon connection status: ' + str(_online_status))
    if not _online_status:  # if no daemon online
        logger.log(
            f"No daemon running at {daemon_config['server']}:{daemon_config['port']}, trying to create daemon..."
        )

        popen = DaemonableProcess(
            target='neetbox.daemon._daemon_launcher',
            args=['--config', json.dumps(daemon_config)],
            mode='detached',
            redirect_stdout=None,
            env_append={'NEETBOX_DAEMON_PROCESS': '1'},
        ).start()

        time.sleep(1)
        _retry = 3
        while not connect_daemon(daemon_config):  # try connect daemon
            logger.warn(f"Could not connect to the daemon. {_retry} retries remaining.")
            time.sleep(1)
            _retry -= 1
            if not _retry:
                logger.err(
                    "Connect daemon faild after 3 retries, daemon connector won't start."
                )
                return False
        return True


def _try_attach_daemon():
    from neetbox.config import get_module_level_config

    _cfg = get_module_level_config()
    if _cfg["enable"]:
        __attach_daemon(_cfg)


__all__ = ["watch", "listen", "_try_attach_daemon"]
