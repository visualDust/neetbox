# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20230414

import setproctitle
import uvicorn

from neetbox._protocol import *


def server_process(cfg, debug=False):
    setproctitle.setproctitle("NEETBOX SERVER")
    from neetbox.logging import Logger

    from ._bridge import Bridge
    from .fastapi import serverapp

    logger = Logger("SERVER LAUNCHER", skip_writers_names=["ws"])
    # load bridges
    Bridge.load_histories()  # load history files

    port = cfg["port"]
    logger.log(f"launching fastapi server on port {port}")
    uvicorn_log_level = "info" if debug else "critical"
    uvicorn.run(serverapp, host="0.0.0.0", port=port, log_level=uvicorn_log_level)
