# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

from neetbox.daemon._daemon_client import connect_daemon, watch
from neetbox.daemon._daemon import daemon_process
from neetbox.logging import logger
from neetbox.integrations import pkg
import time
import os


def __attach_daemon(daemon_config):
    try:
        __IPYTHON__
    except NameError:
        pass
    else:
        logger.log(f"NEETBOX DAEMON won't start when debugging in ipython console.")
        return False  # ignore if debugging in ipython
    _online_status = connect_daemon(daemon_config)  # try to connect daemon
    if not _online_status:  # if no daemon online
        logger.log(
            f"No daemon running at {daemon_config['server']}:{daemon_config['port']}, trying to create daemon..."
        )
        try:
            pid = os.fork()
        except Exception as e:
            logger.err(
                f"Could not fork subprocess because {e}. NEETBOX daemon won't work on Windows."
            )
            return False  # do not run if could not fork
        if pid <= 0:  # child process
            assert pkg.is_installed(
                "daemon", try_install_if_not="python-daemon"
            ), "'python-daemon' is not installed, which is necessary for creating NEETBOX DAEMON"
            try:
                import daemon
            except Exception as e:
                logger.err(
                    f"Package 'python-daemon' not working because {e}. NEETBOX daemon won't work on Windows."
                )
                return False  # do not run if on windows
            with daemon.DaemonContext():
                daemon_process(daemon_config)  # create daemon
        time.sleep(1)
        _retry = 3
        while not connect_daemon(daemon_config):  # try connect daemon
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


__all__ = ["watch", "_try_attach_daemon"]
