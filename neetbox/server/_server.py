# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20230414

import setproctitle

from neetbox._protocol import *
from neetbox.server._bridge import Bridge
from neetbox.server._flask_server import get_flask_server
from neetbox.server._websocket_server import get_web_socket_server


def server_process(cfg, debug=False):
    setproctitle.setproctitle("NEETBOX SERVER")
    from neetbox.logging import LogStyle
    from neetbox.logging.logger import Logger

    logger = Logger("NEETBOX", LogStyle(skip_writers=["ws"]))
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

    port = cfg["port"]
    logger.log(f"launching flask server on port {port}")
    flask_server.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    server_process(
        {
            "port": 5000,
        },
        debug=True,
    )
