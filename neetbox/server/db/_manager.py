# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231201

import atexit
from collections import defaultdict
from typing import Dict

from vdtoys.framing import get_caller_info_traceback
from vdtoys.mvc import Singleton

from neetbox.logging import Logger

from .abc import ManageableDB

logger = Logger("DB Conn Manager", skip_writers_names=["ws"])

ModuleNameType = str
DbIdType = str


class DBConnectionManager(metaclass=Singleton):
    _POOL: Dict[ModuleNameType, Dict[DbIdType, ManageableDB]] = defaultdict(dict)

    @property
    def current(self):
        identity = get_caller_info_traceback(stack_offset=2)
        return self._POOL[identity.module_name]


manager = DBConnectionManager()


def clear_dbc_on_exit():
    logger.info("process exiting, cleaning up...")
    for module_name, conn_dict in manager._POOL.items():
        logger.info(f"closing db connection for module {module_name}:")
        dbc: ManageableDB
        for _, dbc in conn_dict.items():
            logger.info(f"=> closing {dbc}")
            try:
                dbc.close()
            except Exception as e:
                logger.err(RuntimeError(f"failed to close db connection {dbc}, {e}"))


atexit.register(clear_dbc_on_exit)
