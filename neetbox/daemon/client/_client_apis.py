# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414


from neetbox.config import get_module_level_config
from neetbox.daemon.client._connection import connection
from neetbox.logging import logger
from neetbox.utils import pkg
from neetbox.utils.framing import get_frame_module_traceback

module_name = get_frame_module_traceback().__name__  # type: ignore
assert pkg.is_installed(
    "httpx", try_install_if_not=True
), f"{module_name} requires httpx which is not installed"

logger = logger("NEETBOX DAEMON API")

__cfg = get_module_level_config()
daemon_address = f"{__cfg['host']}:{__cfg['port']}"
base_addr = f"http://{daemon_address}"


def get_status_of(name=None):
    name = name or ""
    api_addr = f"{base_addr}/web/list"
    logger.info(f"Fetching from {api_addr}")
    r = connection.http.get(api_addr)
    _data = r.json()
    return _data
