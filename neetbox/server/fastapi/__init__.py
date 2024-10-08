# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20240109

import os
import time
from threading import Thread

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse, RedirectResponse

import neetbox
from neetbox._protocol import *
from neetbox.logging import Logger, LogLevel

from .routers import project as project_router
from .routers import server as server_router

logger = Logger("FASTAPI", skip_writers_names=["ws"])
logger.log_level = LogLevel.DEBUG

serverapp = FastAPI()

front_end_dist_path = os.path.join(os.path.dirname(neetbox.__file__), "frontend_dist")
logger.info(f"using frontend dist path {front_end_dist_path}")

serverapp.include_router(
    project_router.crud_router,
    prefix=f"{API_ROOT}/{PROJECT_KEY}",
    tags=["project"],
)

serverapp.include_router(
    project_router.ws_router,
    prefix=f"{WS_ROOT}/{PROJECT_KEY}",
    tags=["websocket"],
)

serverapp.include_router(
    server_router.crud_router,
    prefix=f"{API_ROOT}/{SERVER_KEY}",
    tags=["server"],
)

serverapp.include_router(
    server_router.ws_router,
    prefix=f"{WS_ROOT}/{SERVER_KEY}",
    tags=["websocket"],
)

# mount web static files root
serverapp.mount("/static", StaticFiles(directory=front_end_dist_path), name="static")


@serverapp.get("/")
def redirect_to_web():
    return RedirectResponse(url="/web/", status_code=301)


@serverapp.get("/web/{path:path}")
async def serve_static_root(path: str):
    # Try to return the requested file
    path = "index.html" if not path else path
    static_file_path = f"{front_end_dist_path}/{path}"
    if os.path.isfile(static_file_path):
        return FileResponse(static_file_path)
    else:
        return FileResponse(f"{front_end_dist_path}/index.html")
