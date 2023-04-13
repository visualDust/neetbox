# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230413

from enum import Enum
from neetbox.logging import logger
import importlib
from typing import List,Optional

class Engine(Enum):
    Torch = "torch"
    
    def __str__(self) -> str:
        return self.value

supported_engines:Optional[List]= None
installed_engines:Optional[List] = None

# todo migrate to python 3.9 after frameworks are supporting it
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
                logger.info(f'\'{engine.vaule}\' was found installed.')
            except:
                pass
    return installed_engines.copy()
