# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20240120

import os
import socket
import time
from threading import Thread

from fastapi import APIRouter

import neetbox
from neetbox._protocol import *
from neetbox.config.user import get as get_global_config
from neetbox.logging import Logger, LogLevel

from ._monitor import disks

logger = Logger("Project APIs", skip_writers_names=["ws"])
logger.log_level = LogLevel.DEBUG

router = APIRouter()


@router.get("/hello")
async def just_send_hello():
    return {"hello": "hello"}


@router.get("/listips")
async def list_server_ips():
    local_hostname = socket.gethostname()
    ip_addresses = socket.gethostbyname_ex(local_hostname)[2]
    filtered_ips = [ip for ip in ip_addresses if not ip.startswith("127.")]
    return {"hostname": local_hostname, "ips": filtered_ips}


@router.post(f"/shutdown")
async def shutdown_server():
    def __sleep_and_shutdown(secs=1):
        time.sleep(secs)
        os._exit(0)

    Thread(target=__sleep_and_shutdown).start()  # shutdown after 3 seconds
    logger.info(f"BYE.")
    return {RESULT_KEY: f"shutdown in 1 seconds."}


@router.get("/configs")
async def get_configs():
    return get_global_config()


_disk_info = None


def update_disk_info():  # todo
    global _disk_info
    while True:
        _disk_info = disks.json
        time.sleep(300)  # update every 5 minutes


Thread(target=update_disk_info).start()


@router.get("/diskusage")
async def get_disk_usgae():
    return _disk_info
