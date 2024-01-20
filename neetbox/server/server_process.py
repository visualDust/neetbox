# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20230414

import setproctitle
import uvicorn
from rich.console import Console
from rich.table import Table

from neetbox._protocol import *

console = Console()


def server_process(cfg, debug=False):
    setproctitle.setproctitle("NEETBOX SERVER")
    from neetbox.logging import Logger

    from .fastapi import serverapp

    logger = Logger("SERVER LAUNCHER", skip_writers_names=["ws"])

    port = cfg["port"]
    logger.log(f"launching fastapi server on http://0.0.0.0:{port}")
    uvicorn_log_level = "info" if debug else "critical"

    table = Table(title="Server Routes")
    table.add_column("name", style="green", no_wrap=True)
    table.add_column("path")
    for name, path in [(route.name, route.path) for route in serverapp.routes]:
        table.add_row(name, path)
    console.print(table)
    uvicorn.run(serverapp, host="0.0.0.0", port=port, log_level=uvicorn_log_level)
