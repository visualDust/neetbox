# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230413

import importlib
from enum import Enum
from functools import lru_cache
from typing import List, Optional

from neetbox.logging import logger


class Engine(Enum):
    Torch = "torch"

    def __str__(self) -> str:
        return self.value


supported_engines: Optional[List] = None
installed_engines: Optional[List] = None


@lru_cache
def get_supported_engines():
    global supported_engines
    if not supported_engines:
        supported_engines = []
        for engine in Engine:
            supported_engines.append(engine)
    return supported_engines.copy()


def get_installed_engines():
    global installed_engines
    if not installed_engines:
        logger.info("Scanning installed engines...")
        installed_engines = []
        for engine in get_supported_engines():
            try:
                importlib.import_module(engine.value)
                installed_engines.append(engine)
                logger.info(f"'{engine.vaule}' was found installed.")
            except ImportError:
                pass
    return installed_engines.copy()
