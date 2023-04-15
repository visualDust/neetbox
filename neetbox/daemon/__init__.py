# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

from neetbox.daemon._daemon_client import connect_daemon, watch
from neetbox.daemon._daemon import daemon_process
from neetbox.logging import logger
from neetbox.utils import pkg
import platform
import time
import os


def __attach_daemon(daemon_config):
    if not daemon_config["allowIpython"]:
        try:
            __IPYTHON__
        except NameError:
            pass
        else:
            logger.log(
                "NEETBOX DAEMON won't start when debugging in ipython console. If you want to allow daemon run in "
                "ipython, try to set 'allowIpython' to True."
            )
            return False  # ignore if debugging in ipython
    _online_status = connect_daemon(daemon_config)  # try to connect daemon
    if not _online_status:  # if no daemon online
        logger.log(
            f"No daemon running at {daemon_config['server']}:{daemon_config['port']}, trying to create daemon..."
        )
        if platform.system() == "Windows": # running on windows
            try:
                assert pkg.is_installed('win32api', try_install_if_not='pywin32'), "Please install 'pywin32' before using NEETBOX daemon"
                assert pkg.is_installed('win32serviceutil', try_install_if_not='pypiwin32'), "Please install 'pywin32' before using NEETBOX daemon"
                from neetbox.daemon._win_service import installService
                installService(cfg=daemon_config)
            except Exception as e:
                logger.err(f"Could not install Windows service because {e}.")
                return False
        else: # not on windows 
            pid = os.fork()
            if pid == 0:  # child process
                pkg.is_installed('daemon', try_install_if_not='python-daemon')
                import daemon
                with daemon.DaemonContext():
                    daemon_process(daemon_config)  # create daemon
            elif pid < 0:
                logger.err(
                    "Faild to spawn daemon process using os.fork. NEETBOX daemon will not start."
                )
                return False
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


__all__ = ["watch", "_try_attach_daemon"]
