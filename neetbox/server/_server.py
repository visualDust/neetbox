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
    from neetbox.logging import LogStyle
    from neetbox.logging.logger import Logger

    from ._bridge import Bridge
    from .fastapi import serverapp
    from .websocket import get_web_socket_server

    logger = Logger("SERVER LAUNCHER", LogStyle(skip_writers=["ws"]))
    # load bridges
    Bridge.load_histories()  # load history files

    # websocket server
    ws_server = get_web_socket_server(config=cfg, debug=debug)
    Bridge._ws_server = ws_server  # add websocket server to bridge

    # launch
    logger.log(f"launching websocket server...")
    ws_server.run_forever(threaded=True)

    port = cfg["port"]
    logger.log(f"launching flask server on port {port}")
    uvicorn.run(serverapp, host="0.0.0.0", port=port, log_level="critical")
