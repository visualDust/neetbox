# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

import setproctitle

from neetbox.daemon._protocol import *
from neetbox.daemon.server._bridge import Bridge
from neetbox.daemon.server._flask_server import get_flask_server
from neetbox.daemon.server._websocket_server import get_web_socket_server
from neetbox.logging import LogStyle, logger

from .history import *

__PROC_NAME = "NEETBOX SERVER"
logger = logger(__PROC_NAME, LogStyle(skip_writers=["ws"]))


def server_process(cfg, debug=False):
    setproctitle.setproctitle(__PROC_NAME)

    # load bridges
    Bridge.load_histories()  # load history files

    # websocket server
    ws_server = get_web_socket_server(config=cfg, debug=debug)
    Bridge._ws_server = ws_server  # add websocket server to bridge

    # http server
    flask_server = get_flask_server(debug=debug)

    # launch
    logger.log(f"launching websocket server...")
    ws_server.run_forever(threaded=True)

    _port = cfg["port"]
    logger.log(f"visit frontend at http://localhost:{_port}")
    flask_server.run(host="0.0.0.0", port=_port)


if __name__ == "__main__":
    server_process(
        {
            "port": 5000,
        },
        debug=True,
    )
