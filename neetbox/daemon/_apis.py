# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230414

from neetbox.config import get_module_level_config
from neetbox.logging import logger
import requests
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
    r = requests.get(api_addr)
    _data = r.json()
    return _data