# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414


from neetbox.utils import pkg
from neetbox.utils.framing import get_frame_module_traceback
from neetbox.daemon._local_http_client import _local_http_client
module_name = get_frame_module_traceback().__name__
assert pkg.is_installed('httpx', try_install_if_not=True), f"{module_name} requires httpx which is not installed"
import httpx
from neetbox.config import get_module_level_config
from neetbox.logging import logger
import time
import json
logger = logger("NEETBOX DAEMON API")

__cfg = get_module_level_config()
daemon_address = f"{__cfg['server']}:{__cfg['port']}"
base_addr = f"http://{daemon_address}"
    
def get_status_of(name=None):
    name = name or ""
    api_addr = f"{base_addr}/status"
    logger.info(f"Fetching from {api_addr}")
    r = _local_http_client.get(api_addr)
    _data = r.json()
    return _data