# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20240120

import os
import time
from threading import Thread

from fastapi import APIRouter

from neetbox._protocol import *
from neetbox.logging import Logger, LogLevel

logger = Logger("Project APIs", skip_writers_names=["ws"])
logger.log_level = LogLevel.DEBUG

router = APIRouter()


@router.get("/hello")
async def just_send_hello():
    return {"hello": "hello"}


@router.post(f"/shutdown")
async def shutdown_server():
    def __sleep_and_shutdown(secs=1):
        time.sleep(secs)
        os._exit(0)

    Thread(target=__sleep_and_shutdown).start()  # shutdown after 3 seconds
    logger.info(f"BYE.")
    return {RESULT_KEY: f"shutdown in 1 seconds."}
