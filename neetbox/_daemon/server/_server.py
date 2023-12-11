# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

import setproctitle

from neetbox._daemon._protocol import *
from neetbox._daemon.server._bridge import Bridge
from neetbox._daemon.server._flask_server import get_flask_server
from neetbox._daemon.server._websocket_server import get_web_socket_server
from neetbox._daemon.server.history import *


def server_process(cfg, debug=False):
    setproctitle.setproctitle("NEETBOX SERVER")
    from neetbox.logging import LogStyle, logger

    logger = logger("NEETBOX", LogStyle(skip_writers=["ws"]))

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
